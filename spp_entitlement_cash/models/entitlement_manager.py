# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class EntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager"
    _description = "Cash Entitlement Manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.cash", "Cash")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class G2PCashEntitlementManager(models.Model):
    """
    G2PCashEntitlementManager is the model for the cash entitlement manager.
    It provides all the functions for processing cash entitlements.

    """

    _name = "g2p.program.entitlement.manager.cash"
    _inherit = [
        "g2p.base.program.entitlement.manager",
        "g2p.manager.source.mixin",
    ]
    _description = "Cash Entitlement Manager"

    # Set to True so that the UI will display the payment management components
    IS_CASH_ENTITLEMENT = True

    # Cash Entitlement Manager
    evaluate_one_item = fields.Boolean(default=False)
    entitlement_item_ids = fields.One2many(
        "g2p.program.entitlement.manager.cash.item",
        "entitlement_id",
        "Entitlement Items",
    )
    max_amount = fields.Monetary(
        string="Maximum Amount",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="program_id.journal_id.currency_id",
        readonly=True,
    )

    # Group able to validate the payment
    # Todo: Create a record rule for payment_validation_group
    entitlement_validation_group_id = fields.Many2one("res.groups", string="Entitlement Validation Group")

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare Cash Entitlements.
        Cash Entitlement Manager :meth:`prepare_entitlements`.
        This method is used to prepare the entitlement list of the beneficiaries.

        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return:
        """
        if not self.entitlement_item_ids:
            raise UserError(_("There are no items entered for this entitlement manager."))

        all_beneficiaries_ids = beneficiaries.mapped("partner_id.id")

        new_entitlements_to_create = {}
        for rec in self.entitlement_item_ids:
            _logger.info(f"Rec Amount: {rec.amount}")
            if rec.condition:
                beneficiaries_ids = self._get_all_beneficiaries(
                    all_beneficiaries_ids, rec.condition, self.evaluate_one_item
                )
            else:
                beneficiaries_ids = all_beneficiaries_ids

            beneficiaries_with_entitlements = (
                self.env["g2p.entitlement"]
                .search(
                    [
                        ("cycle_id", "=", cycle.id),
                        ("partner_id", "in", beneficiaries_ids),
                    ]
                )
                .mapped("partner_id.id")
            )
            entitlements_to_create = [
                beneficiaries_id
                for beneficiaries_id in beneficiaries_ids
                if beneficiaries_id not in beneficiaries_with_entitlements
            ]

            entitlement_start_validity = cycle.start_date
            entitlement_end_validity = cycle.end_date
            entitlement_currency = rec.currency_id.id

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(entitlements_to_create)

            for beneficiary_id in beneficiaries_with_entitlements_to_create:
                if rec.multiplier_field:
                    # Get the multiplier value from multiplier_field else return the default multiplier=1
                    multiplier = beneficiary_id.mapped(rec.multiplier_field.name)
                    if multiplier:
                        multiplier = multiplier[0] or 0
                else:
                    multiplier = 1
                if rec.max_multiplier > 0 and multiplier > rec.max_multiplier:
                    multiplier = rec.max_multiplier
                amount = rec.amount * float(multiplier)

                # Compute the sum of cash entitlements
                if beneficiary_id.id in new_entitlements_to_create:
                    amount = amount + new_entitlements_to_create[beneficiary_id.id]["initial_amount"]
                # Check if amount > max_amount; ignore if max_amount is set to 0
                if self.max_amount > 0.0 and amount > self.max_amount:
                    amount = self.max_amount

                new_entitlements_to_create[beneficiary_id.id] = {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "initial_amount": amount,
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }
                # Check if there are additional fields to be added in entitlements
                addl_fields = self._get_addl_entitlement_fields(beneficiary_id)
                if addl_fields:
                    new_entitlements_to_create[beneficiary_id.id].update(addl_fields)

        # Create entitlement records
        for ent in new_entitlements_to_create:
            initial_amount = new_entitlements_to_create[ent]["initial_amount"]
            new_entitlements_to_create[ent]["initial_amount"] = self._check_subsidy(initial_amount)
            # Create non-zero entitlements only
            if new_entitlements_to_create[ent]["initial_amount"] > 0.0:
                self.env["g2p.entitlement"].create(new_entitlements_to_create[ent])

    def _get_addl_entitlement_fields(self, beneficiary_id):
        """
        This function must be overriden to add additional field to be written in the entitlements.
        Add the id_number from the beneficiaries based on the id_type configured in entitlement manager.
        """
        retval = None
        if self.id_type:
            id_docs = beneficiary_id.reg_ids.filtered(lambda a: a.id_type.id == self.id_type.id)
            if id_docs:
                id_number = id_docs[0].value
                retval = {
                    "id_number": id_number,
                }
        return retval

    def _get_all_beneficiaries(self, all_beneficiaries_ids, condition, evaluate_one_item):
        """Get All Beneficiaries.
        Cash Entitlement Manager :meth:`_get_all_beneficiaries`.
        Called by :meth:`prepare_entitlements` to get all beneficiaries to be prepared entitlements.

        :param all_beneficiaries_ids: Recordset of beneficiaries
        :param condition: List of tuple of domain filter
        :param evaluate_one_item: Boolean if true will evaluate all beneficiaries if it should be removed
        :return: all_beneficiaries_ids: recordset of beneficiaries
        """
        # Filter res.partner based on entitlement condition and get ids
        domain = [("id", "in", all_beneficiaries_ids)]
        domain += self._safe_eval(condition)
        beneficiaries_ids = self.env["res.partner"].search(domain).ids
        # Check if single evaluation
        if evaluate_one_item:
            # Remove beneficiaries_ids from all_beneficiaries_ids
            for bid in beneficiaries_ids:
                if bid in all_beneficiaries_ids:
                    all_beneficiaries_ids.remove(bid)
        return all_beneficiaries_ids

    def _check_subsidy(self, amount):
        # Check if initial_amount > max_amount then set = max_amount
        # Ignore if max_amount is set to 0
        if self.max_amount > 0.0 and amount > self.max_amount:
            return self.max_amount
        return amount

    def set_pending_validation_entitlements(self, cycle):
        """Set Cash Entitlements to Pending Validation.
        Cash Entitlement Manager :meth:`set_pending_validation_entitlements`.
        Set entitlements to pending_validation in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements in cycle
        entitlements = cycle.get_entitlements(
            ["draft"],
            entitlement_model="g2p.entitlement",
        )
        entitlements_count = len(entitlements)
        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            self._set_pending_validation_entitlements(entitlements)

        else:
            self._set_pending_validation_entitlements_async(cycle, entitlements)

    def _set_pending_validation_entitlements(self, entitlements):
        """Set Cash Entitlements to Pending Validation.
        Cash Entitlement Manager :meth:`_set_pending_validation_entitlements`.
        Set entitlements to pending_validation in a cycle.

        :param entitlements: A recordset of entitlements to process
        :return:
        """
        entitlements.update({"state": "pending_validation"})
        _logger.debug("Entitlement Validation: total: %s" % (len(entitlements)))

    def validate_entitlements(self, cycle):
        """Validate Cash Entitlements.
        Cash Entitlement Manager :meth:`validate_entitlements`.
        Validate entitlements in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements in cycle
        entitlements = cycle.get_entitlements(
            ["draft", "pending_validation"],
            entitlement_model="g2p.entitlement",
        )
        entitlements_count = len(entitlements)
        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            err, message = self._validate_entitlements(cycle, entitlements)
            if err > 0:
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Entitlement"),
                        "message": message,
                        "sticky": True,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }
            else:
                kind = "success"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Entitlement"),
                        "message": _("Entitlements are validated and approved."),
                        "sticky": True,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }
        else:
            self._validate_entitlements_async(cycle, entitlements, entitlements_count)

    def _validate_entitlements_async(self, cycle, entitlements, entitlements_count):
        """Validate Entitlements.
        Cash Entitlement Manager :meth:`_validate_entitlements_async`.
        Asynchronous validation of entitlements in a cycle using `job_queue`.
        Needs to override this method because the call to sef.delayable()._validate entitlements
        needs the cycle in the parameter.

        :param cycle: A recordset of cycle
        :param entitlements: A recordset of entitlements to validate
        :param entitlements_count: Integer count of entitlements to validate
        :return:
        """
        _logger.debug("Validate entitlements asynchronously")
        cycle.message_post(body=_("Validate %s entitlements started.", entitlements_count))
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Validate and approve entitlements for cycle."),
            }
        )

        jobs = []
        for i in range(0, entitlements_count, self.MAX_ROW_JOB_QUEUE):
            # Needs to override
            jobs.append(self.delayable()._validate_entitlements(cycle, entitlements[i : i + self.MAX_ROW_JOB_QUEUE]))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Entitlements Validated and Approved.")))
        main_job.delay()

    def _validate_entitlements(self, cycle, entitlements):
        """Validate Cash Entitlements.
        Cash Entitlement Manager :meth:`_validate_entitlements`.
        Validate entitlements in a cycle.

        :param cycle: A recordset of cycle
        :param entitlements: A recordset of entitlements to validate
        :return err: Integer number of errors
        :return message: String description of the error
        """
        err, message = self.approve_entitlements(entitlements)
        if err:
            cycle.message_post(body=_(message))
            cycle.write({"validate_async_err": True, "state": "to_approve"})
        else:
            cycle.write({"validate_async_err": False})
        return err, message

    def mark_job_as_done(self, cycle, msg):
        if cycle.validate_async_err:
            msg = _("Entitlements are not approved due to some issues. Kindly address the issue.")
        super().mark_job_as_done(cycle, msg)

        return

    def cancel_entitlements(self, cycle):
        """Cancel Cash Entitlements.
        Cash Entitlement Manager :meth:`cancel_entitlements`.
        Cancel entitlements in a cycle.

        :param cycle: A recordset of cycle
        :return:
        """
        # Get the number of entitlements in cycle
        entitlements = cycle.get_entitlements(
            ["draft", "pending_validation", "approved"],
            entitlement_model="g2p.entitlement",
        )
        entitlements_count = len(entitlements)
        if entitlements_count < self.MIN_ROW_JOB_QUEUE:
            self._cancel_entitlements(entitlements)
        else:
            self._cancel_entitlements_async(cycle, entitlements, entitlements_count)

    def _cancel_entitlements(self, entitlements):
        """Cancel Cash Entitlements.
        Cash Entitlement Manager :meth:`_cancel_entitlements`.
        Cancel entitlements in a cycle.

        :param entitlements: A recordset of entitlements to cancel
        :return:
        """
        entitlements.update({"state": "cancelled"})

    def approve_entitlements(self, entitlements):
        """Approve Cash Entitlements.
        Cash Entitlement Manager :meth:`_approve_entitlements`.
        Approve selected entitlements.

        :param entitlements: Selected entitlements to approve
        :return state_err: Integer number of errors
        :return message: String description of the errors
        """
        amt = 0.0
        state_err = 0
        message = ""
        sw = 0
        for rec in entitlements:
            if rec.state in ("draft", "pending_validation"):
                fund_balance = self.check_fund_balance(rec.cycle_id.program_id.id) - amt
                if fund_balance >= rec.initial_amount:
                    amt += rec.initial_amount
                    # Prepare journal entry (account.move) via account.payment
                    amount = rec.initial_amount
                    new_service_fee = None
                    if rec.transfer_fee > 0.0:
                        amount -= rec.transfer_fee
                        # Incurred Fees (transfer fees)
                        payment = {
                            "partner_id": rec.partner_id.id,
                            "payment_type": "outbound",
                            "amount": rec.transfer_fee,
                            "currency_id": rec.journal_id.currency_id.id,
                            "journal_id": rec.journal_id.id,
                            "partner_type": "supplier",
                            "ref": "Service Fee: Code: %s" % rec.code,
                        }
                        new_service_fee = self.env["account.payment"].create(payment)

                    # Fund Disbursed (amount - transfer fees)
                    payment = {
                        "partner_id": rec.partner_id.id,
                        "payment_type": "outbound",
                        "amount": amount,
                        "currency_id": rec.journal_id.currency_id.id,
                        "journal_id": rec.journal_id.id,
                        "partner_type": "supplier",
                        "ref": "Fund disbursed to beneficiary: Code: %s" % rec.code,
                    }
                    new_payment = self.env["account.payment"].create(payment)

                    rec.update(
                        {
                            "disbursement_id": new_payment.id,
                            "service_fee_disbursement_id": new_service_fee and new_service_fee.id or None,
                            "state": "approved",
                            "date_approved": fields.Date.today(),
                        }
                    )
                else:
                    message = _(
                        "The fund for the program: %(program)s [%(fund).2f] "
                        + "is insufficient for the entitlement: %(entitlement)s"
                    ) % {
                        "program": rec.cycle_id.program_id.name,
                        "fund": fund_balance,
                        "entitlement": rec.code,
                    }
                    # Stop the process and return an error
                    return (1, message)
            else:
                state_err += 1
                if sw == 0:
                    sw = 1
                    message = _("Entitlement State Error! Entitlements not in 'pending validation' state:\n")
                message += _("Program: %(prg)s, Beneficiary: %(partner)s.\n") % {
                    "prg": rec.cycle_id.program_id.name,
                    "partner": rec.partner_id.name,
                }

        return (state_err, message)

    def open_entitlements_form(self, cycle):
        self.ensure_one()
        action = {
            "name": _("Cash Entitlements"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.entitlement",
            "context": {
                "create": False,
                "default_cycle_id": cycle.id,
                # "search_default_approved_state": 1,
            },
            "view_mode": "list,form",
            "views": [
                [self.env.ref("g2p_programs.view_entitlement_tree").id, "tree"],
                [self.env.ref("g2p_programs.view_entitlement_form").id, "form"],
            ],
            "domain": [("cycle_id", "=", cycle.id)],
        }
        return action

    def open_entitlement_form(self, rec):
        return {
            "name": "Cash Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement",
            "res_id": rec.id,
            "view_id": self.env.ref("g2p_programs.view_entitlement_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
        }


class G2PCashEntitlementItem(models.Model):
    _name = "g2p.program.entitlement.manager.cash.item"
    _description = "Cash Entitlement Manager Items"
    _order = "sequence,id"

    sequence = fields.Integer(default=1000)
    entitlement_id = fields.Many2one("g2p.program.entitlement.manager.cash", "Cash Entitlement", required=True)

    amount = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
        string="Amount per cycle",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="entitlement_id.program_id.journal_id.currency_id",
        readonly=True,
    )

    # non-mandatory field to store a domain that is used to verify if this item is valid for a beneficiary
    # For example, it could be: [('is_woman_headed_household, '=', True)]
    # If the condition is not met, this calculation is not used
    condition = fields.Char("Condition Domain")

    # `multiplier_field` can be any integer field of `res.partner`
    # It could be the number of members, children, elderly, or any other metrics.
    multiplier_field = fields.Many2one(
        "ir.model.fields",
        "Multiplier",
        domain=[("model_id.model", "=", "res.partner"), ("ttype", "=", "integer")],
    )
    max_multiplier = fields.Integer(
        default=0,
        string="Maximum number",
        help="0 means no limit",
    )
