# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
# import base64
# import csv
# from io import StringIO
import logging
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class PaymentManager(models.Model):
    _name = "g2p.program.payment.manager"
    _description = "Payment Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program", ondelete="cascade")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.payment.manager.default", "Default")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BasePaymentManager(models.AbstractModel):
    _name = "g2p.base.program.payment.manager"
    _inherit = "base.programs.manager"
    _description = "Base Payment Manager"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def prepare_payments(self, entitlements):
        """
        This method is used to prepare the payment list of the entitlements.
        :param entitlements: The entitlements.
        :return:
        """
        raise NotImplementedError()

    def send_payments(self, batches):
        """
        This method is used to send the payment list by batch.
        :param batches: The payment batches.
        :return:
        """
        raise NotImplementedError()

    def validate_accounts(self, entitlements):
        """
        This method is used to that accounts exist to pay the entitlements
        :param entitlements: The list of entitlements
        :return:
        """
        raise NotImplementedError()

    def mark_job_as_done(self, cycle, msg):
        """
        Base :meth:`mark_job_as_done`
        Post a message in the chatter

        :param cycle: A recordset of cycle
        :param msg: A string to be posted in the chatter
        :return:
        """
        self.ensure_one()
        cycle.locked = False
        cycle.locked_reason = None
        cycle.message_post(body=msg)


class DefaultFilePaymentManager(models.Model):
    _name = "g2p.program.payment.manager.default"
    _inherit = ["g2p.base.program.payment.manager", "g2p.manager.source.mixin"]
    _description = "Default Payment Manager"

    MAX_PAYMENTS_FOR_SYNC_PREPARE = 200
    MAX_BATCHES_FOR_SYNC_SEND = 50

    currency_id = fields.Many2one("res.currency", related="program_id.journal_id.currency_id", readonly=True)

    create_batch = fields.Boolean("Automatically Create Batch")

    batch_tag_ids = fields.Many2many(
        "g2p.payment.batch.tag",
        "g2p_pay_batch_tag_pay_manager_def",
        string="Batch Tags",
        ondelete="cascade",
    )
    # batch_tag_ids = fields.One2many("g2p.payment.batch.tag",
    # "default_payment_manager_id", string="Batch Tags")

    @api.onchange("create_batch")
    def on_change_create_batch(self):
        if self.create_batch:
            existing_batch = (
                self.env["g2p.payment.batch.tag"]
                .sudo()
                .search(
                    [
                        ("name", "=", f"Default {self.program_id.name}"),
                        ("order", "=", 1),
                        ("max_batch_size", "=", 500),
                    ],
                    limit=1,
                )
            )

            if existing_batch:
                batch_id = existing_batch
            else:
                batch_id = (
                    self.env["g2p.payment.batch.tag"]
                    .sudo()
                    .create(
                        {
                            "name": f"Default {self.program_id.name}",
                            "order": 1,
                            "domain": [],
                            "max_batch_size": 500,
                        }
                    )
                )

            self.batch_tag_ids = [(4, batch_id.id)]
        else:
            self.batch_tag_ids = [(5,)]

    @api.constrains("batch_tag_ids")
    def constrains_batch_tag_ids(self):
        for rec in self:
            if rec.create_batch:
                if not len(rec.batch_tag_ids):
                    raise ValidationError(_("Batch Tags list cannot be empty."))
                if rec.batch_tag_ids.sorted("order")[-1].domain != "[]":
                    raise ValidationError(_("Last tag in the Batch Tags list must contain empty domain."))

    def prepare_payments(self, cycle, entitlements=None):
        if not entitlements:
            entitlements = cycle.entitlement_ids.filtered(lambda a: a.state == "approved")
        else:
            entitlements = entitlements.filtered(lambda a: a.state == "approved")
        entitlements_count = len(entitlements)
        if entitlements_count:
            if entitlements_count < self.MAX_PAYMENTS_FOR_SYNC_PREPARE:
                payments, batches = self._prepare_payments(cycle, entitlements)
                if payments:
                    kind = "success"
                    message = _(
                        "Payment batch successfully created for %s beneficiaries.",
                        len(payments),
                    )
                    sticky = False
                else:
                    kind = "danger"
                    message = _("There are no new payments issued!")
                    sticky = False
            else:
                self._prepare_payments_async(cycle, entitlements, entitlements_count)
                kind = "success"
                message = _("Preparing Payments Asynchronously.")
                sticky = True
        else:
            kind = "danger"
            message = _("All entitlements selected are not approved!")
            sticky = False

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Payment"),
                "message": message,
                "sticky": sticky,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def _prepare_payments(self, cycle, entitlements):
        if not entitlements:
            return None, None
        # Filter out entitlements without payments
        entitlements = entitlements.filtered(
            lambda x: x.state == "approved" and all(payment.status == "failed" for payment in x.payment_ids)
        )

        is_create_batch = self.create_batch

        # payments is a recordset of g2p.payment
        # batches is a recordset of g2p.payment.batch
        # curr_batch is loop variable.
        payments = None
        batches = None
        curr_batch = None
        for batch_tag in self.batch_tag_ids:
            domain = self._safe_eval(batch_tag.domain)
            # The following filtered_domain line is causing a problem in a particular use case
            # hence using another way for now
            # tag_entitlements = entitlements.filtered_domain(domain)
            tag_entitlements = entitlements & entitlements.search(domain)
            entitlements -= tag_entitlements
            max_batch_size = batch_tag.max_batch_size

            for i, entitlement_id in enumerate(tag_entitlements):
                payment = self.env["g2p.payment"].create(
                    {
                        "name": str(uuid4()),
                        "entitlement_id": entitlement_id.id,
                        "cycle_id": entitlement_id.cycle_id.id,
                        "amount_issued": entitlement_id.initial_amount,
                        "payment_fee": entitlement_id.transfer_fee,
                        "state": "issued",
                    }
                )
                if payment.partner_id.bank_ids:
                    payment.account_number = payment.partner_id.bank_ids[0].acc_number
                else:
                    payment.account_number = None

                if not payments:
                    payments = payment
                else:
                    payments += payment
                if is_create_batch:
                    if i % max_batch_size == 0:
                        curr_batch = self.env["g2p.payment.batch"].create(
                            {
                                "name": str(uuid4()),
                                "cycle_id": cycle.id,
                                "stats_datetime": fields.Datetime.now(),
                                "tag_id": batch_tag.id,
                            }
                        )
                        if not batches:
                            batches = curr_batch
                        else:
                            batches += curr_batch
                    curr_batch.payment_ids = [(4, payment.id)]
                    payment.batch_id = curr_batch
        return payments, batches

    def _prepare_payments_async(self, cycle, entitlements, entitlements_count):
        _logger.debug("Prepare Payments asynchronously")
        cycle.message_post(body=_("Prepare payments started for %s entitlements.", entitlements_count))
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Prepare payments for entitlements in cycle."),
            }
        )

        # Right now this is not divided into subjobs
        jobs = [
            self.delayable()._prepare_payments(cycle, entitlements),
        ]
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Prepared payments.")))
        main_job.delay()

    def send_payments(self, batches):
        # TODO: Return client action with proper message.
        batches_count = len(batches)
        if batches_count < self.MAX_BATCHES_FOR_SYNC_SEND:
            return self._send_payments(batches)
        else:
            cycles, cycle_batches = self._group_batches_by_cycle(batches)
            for batches in cycle_batches:
                cycle = batches[0].cycle_id
                self._send_payments_async(cycle, batches)
            message = _("Sending Payments Asynchronously")
            kind = "success"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Payment"),
                    "message": message,
                    "sticky": True,
                    "type": kind,
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

    def _send_payments(self, batches):
        # Create a payment list (CSV)
        # _logger.debug("DEBUG! send_payments Manager: DEFAULT")
        if not batches:
            message = _("No payment batches to process.")
            kind = "warning"

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Payment"),
                    "message": message,
                    "sticky": True,
                    "type": kind,
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }
        # TODO: Removed CSV Creation part after confirmation with team for timebeing.
        # else:
        # for rec in batches:
        #     filename = f"{rec.name}.csv"
        #     data = StringIO()
        #     csv_writer = csv.writer(data, quoting=csv.QUOTE_MINIMAL)
        #     header = [
        #         "row_number",
        #         "internal_payment_reference",
        #         "account_number",
        #         "beneficiary_name",
        #         "amount",
        #         "currency",
        #         "details_of_payment",
        #     ]
        #     csv_writer.writerow(header)
        #     for row, payment_id in enumerate(rec.payment_ids):
        #         account_number = ""
        #         if payment_id.partner_id.bank_ids:
        #             account_number = payment_id.partner_id.bank_ids[0].iban
        #         details_of_payment = (
        #             f"{payment_id.program_id.name} - {payment_id.cycle_id.name}"
        #         )
        #         row = [
        #             row,
        #             payment_id.name,
        #             account_number,
        #             payment_id.partner_id.name,
        #             payment_id.amount_issued,
        #             payment_id.currency_id.name,
        #             details_of_payment,
        #         ]
        #         csv_writer.writerow(row)
        #     csv_data = base64.encodebytes(bytearray(data.getvalue(), "utf-8"))
        #     # Attach the generated CSV to payment batch
        #     self.env["ir.attachment"].create(
        #         {
        #             "name": filename,
        #             "res_model": "g2p.payment.batch",
        #             "res_id": rec.id,
        #             "type": "binary",
        #             "store_fname": filename,
        #             "mimetype": "text/csv",
        #             "datas": csv_data,
        #         }
        #     )
        #     # _logger.debug("DEFAULT Payment Manager: data: %s" % csv_data)
        # message = _("Payment CSV created successfully")
        # kind = "success"

    def _send_payments_async(self, cycle, batches):
        _logger.debug("Send Payments asynchronously")
        cycle.message_post(body=_("Send payments started for %s batches.", len(batches)))
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Send payments for batches in cycle."),
            }
        )

        # Right now this is not divided into subjobs
        jobs = [
            self.delayable()._send_payments(batches),
        ]
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Send payments completed.")))
        main_job.delay()

    @api.model
    def _group_batches_by_cycle(self, batches):
        cycles = set(map(lambda x: x.cycle_id, batches))
        cycle_batches = [batches.filtered_domain([("cycle_id", "=", cycle.id)]) for cycle in cycles]
        return cycles, cycle_batches

    def _get_account_number(self, entitlement):
        return entitlement.partner_id.get_payment_token(entitlement.program_id)
