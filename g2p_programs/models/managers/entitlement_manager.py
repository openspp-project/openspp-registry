# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class EntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager"
    _description = "Entitlement Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program", ondelete="cascade")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.default", "Default")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseEntitlementManager(models.AbstractModel):
    _name = "g2p.base.program.entitlement.manager"
    _inherit = "base.programs.manager"
    _description = "Base Entitlement Manager"

    IS_CASH_ENTITLEMENT = True
    MIN_ROW_JOB_QUEUE = 200
    MAX_ROW_JOB_QUEUE = 2000

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def prepare_entitlements(self, cycle, beneficiaries):
        """
        This method is used to prepare the entitlement list of the beneficiaries.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return entitlements:
        """
        raise NotImplementedError()

    def set_pending_validation_entitlements(self, cycle):
        """Base Entitlement Manager :meth:`set_pending_validate_entitlements`
        Set entitlements to pending_validation in a cycle
        Override in entitlement manager

        :param cycle: A recordset of cycle
        :return:
        """
        raise NotImplementedError()

    def _set_pending_validation_entitlements_async(self, cycle, entitlements):
        """Set Entitlements to Pending Validation
        Base Entitlement Manager :meth:`_set_pending_validation_entitlements_async`
        Asynchronous setting of entitlements to pending_validation in a cycle using `job_queue`

        :param cycle: A recordset of cycle
        :param entitlements: A recordset of entitlements to process
        :return:
        """
        entitlements_count = len(entitlements)
        _logger.debug("Set entitlements to pending validation asynchronously")
        cycle.message_post(
            body=_(
                "Setting %s entitlements to pending validation has started.",
                entitlements_count,
            )
        )
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Set entitlements to pending validation for cycle."),
            }
        )

        jobs = []
        for i in range(0, entitlements_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable()._set_pending_validation_entitlements(
                    entitlements[i : i + self.MAX_ROW_JOB_QUEUE]
                )
            )
        main_job = group(*jobs)
        main_job.on_done(
            self.delayable().mark_job_as_done(cycle, _("Entitlements Set to Pending Validation."))
        )
        main_job.delay()

    def _set_pending_validation_entitlements(self, entitlements):
        """
        Base Entitlement Manager :meth:`_set_pending_validation_entitlements`
        Synchronous setting of entitlements to pending_validation in a cycle
        Override in entitlement manager

        :param entitlements: A recordset of entitlements
        :return:
        """
        raise NotImplementedError()

    def validate_entitlements(self, cycle):
        """Base Entitlement Manager :meth:`validate_entitlements`
        Validate entitlements for a cycle
        Override in entitlement manager

        :param cycle: A recordset of cycle
        :return:
        """
        raise NotImplementedError()

    def _validate_entitlements_async(self, cycle, entitlements, entitlements_count):
        """Validate Entitlements
        Base Entitlement Manager :meth:`_validate_entitlements_async`
        Asynchronous validation of entitlements in a cycle using `job_queue`

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
            jobs.append(self.delayable()._validate_entitlements(entitlements[i : i + self.MAX_ROW_JOB_QUEUE]))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Entitlements Validated and Approved.")))
        main_job.delay()

    def _validate_entitlements(self, entitlements):
        """
        Base Entitlement Manager :meth:`_validate_entitlements`
        Synchronous validation of entitlements in a cycle
        Override in entitlement manager

        :param entitlements: A recordset of entitlements to validate
        :return:
        """
        # Call the program's entitlement manager and validate the entitlements
        # TODO: Use a Job attached to the cycle
        # TODO: Implement validation workflow
        raise NotImplementedError()

    def approve_entitlements(self, entitlements):
        """Base Entitlement Manager :meth:`_approve_entitlements`
        Approve selected entitlements
        Override in entitlement manager

        :param entitlements: Selected entitlements to approve.
        :return:
        """
        raise NotImplementedError()

    def cancel_entitlements(self, cycle):
        """Base Entitlement Manager :meth:`cancel_entitlements`
        Cancel entitlements in a cycle
        Override in entitlement manager

        :param cycle: A recordset of cycle
        :return:
        """
        raise NotImplementedError()

    def _cancel_entitlements_async(self, cycle, entitlements, entitlements_count):
        """Cancel Entitlements
        Base Entitlement Manager :meth:`_cancel_entitlements_async`
        Asynchronous cancellation of entitlements in a cycle using `job_queue`

        :param cycle: A recordset of cycle
        :param entitlements: A recordset of entitlements to cancel
        :param entitlements_count: Integer value of total entitlements to process
        :return:
        """
        _logger.debug("Cancel entitlements asynchronously")
        cycle.message_post(body=_("Cancel %s entitlements started.", entitlements_count))
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Cancel entitlements for cycle."),
            }
        )

        jobs = []
        for i in range(0, entitlements_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(self.delayable()._cancel_entitlements(entitlements[i : i + self.MAX_ROW_JOB_QUEUE]))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_job_as_done(cycle, _("Entitlements Cancelled.")))
        main_job.delay()

    def _cancel_entitlements(self, entitlements):
        """
        Base Entitlement Manager :meth:`_cancel_entitlements`
        Synchronous cancellation of entitlements in a cycle
        Override in entitlement manager

        :param entitlements: A recordset of entitlements to cancel
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

    def open_entitlements_form(self, cycle):
        """
        This method is used to open the list view of entitlements in a cycle.
        :param cycle: The cycle.
        :return:
        """
        raise NotImplementedError()

    def open_entitlement_form(self, rec):
        """
        This method is used to open the form view of a selected entitlement.
        :param rec: The entitlement.
        :return:
        """
        raise NotImplementedError()

    def check_fund_balance(self, program_id):
        company_id = self.env.user.company_id and self.env.user.company_id.id or None
        retval = 0.0
        if company_id:
            params = (
                company_id,
                program_id,
            )

            # Get the current fund balance
            fund_bal = 0.0
            sql = """
                select sum(amount) as total_fund
                from g2p_program_fund
                where company_id = %s
                    AND program_id = %s
                    AND state = 'posted'
                """
            self._cr.execute(sql, params)
            program_funds = self._cr.dictfetchall()
            fund_bal = program_funds[0]["total_fund"] or 0.0

            # Get the current entitlement totals
            total_entitlements = 0.0
            sql = """
                select sum(a.initial_amount) as total_entitlement
                from g2p_entitlement a
                    left join g2p_cycle b on b.id = a.cycle_id
                where a.company_id = %s
                    AND b.program_id = %s
                    AND a.state = 'approved'
                """
            self._cr.execute(sql, params)
            entitlements = self._cr.dictfetchall()
            total_entitlements = entitlements[0]["total_entitlement"] or 0.0

            retval = fund_bal - total_entitlements
        return retval


class DefaultCashEntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager.default"
    _inherit = ["g2p.base.program.entitlement.manager", "g2p.manager.source.mixin"]
    _description = "Default Entitlement Manager"

    # Set to True so that the UI will display the payment management components
    IS_CASH_ENTITLEMENT = True

    amount_per_cycle = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
    )
    amount_per_individual_in_group = fields.Monetary(
        currency_field="currency_id",
        group_operator="sum",
        default=0.0,
    )
    max_individual_in_group = fields.Integer(
        default=0,
        string="Maximum number of individual in group",
        help="0 means no limit",
    )

    currency_id = fields.Many2one("res.currency", related="program_id.journal_id.currency_id", readonly=True)

    # Transfer Fees
    transfer_fee_pct = fields.Float(
        "Transfer Fee(%)",
        digits=(5, 2),
        default=0.0,
        help="Transfer fee will be a percentage of amount",
    )
    transfer_fee_amt = fields.Monetary(
        "Transfer Fee Amount",
        default=0.0,
        currency_field="currency_id",
        help="Set fixed transfer fee amount",
    )

    # Group able to validate the payment
    # Todo: Create a record rule for payment_validation_group
    entitlement_validation_group_id = fields.Many2one("res.groups", string="Entitlement Validation Group")

    @api.onchange("transfer_fee_pct")
    def on_transfer_fee_pct_change(self):
        if self.transfer_fee_pct > 0.0:
            self.transfer_fee_amt = 0.0

    @api.onchange("transfer_fee_amt")
    def on_transfer_fee_amt_change(self):
        if self.transfer_fee_amt > 0.0:
            self.transfer_fee_pct = 0.0

    def prepare_entitlements(self, cycle, beneficiaries):
        """Prepare entitlements.
        This method is used to prepare the entitlement list of the beneficiaries.
        :param cycle: The cycle.
        :param beneficiaries: The beneficiaries.
        :return entitlements:
        """
        benecifiaries_ids = beneficiaries.mapped("partner_id.id")

        benecifiaries_with_entitlements = (
            self.env["g2p.entitlement"]
            .search([("cycle_id", "=", cycle.id), ("partner_id", "in", benecifiaries_ids)])
            .mapped("partner_id.id")
        )
        entitlements_to_create = [
            benecifiaries_id
            for benecifiaries_id in benecifiaries_ids
            if benecifiaries_id not in benecifiaries_with_entitlements
        ]

        entitlement_start_validity = cycle.start_date
        entitlement_end_validity = cycle.end_date
        entitlement_currency = self.currency_id.id

        beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(entitlements_to_create)

        individual_count = beneficiaries_with_entitlements_to_create.count_individuals()
        individual_count_map = dict(individual_count)

        entitlements = []
        for beneficiary_id in beneficiaries_with_entitlements_to_create:
            amount = self._calculate_amount(beneficiary_id, individual_count_map.get(beneficiary_id.id, 0))
            transfer_fee = 0.0
            if self.transfer_fee_pct > 0.0:
                transfer_fee = amount * (self.transfer_fee_pct / 100.0)
            elif self.transfer_fee_amt > 0.0:
                transfer_fee = self.transfer_fee_amt
            entitlements.append(
                {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "initial_amount": amount,
                    "transfer_fee": transfer_fee,
                    "currency_id": entitlement_currency,
                    "state": "draft",
                    "is_cash_entitlement": True,
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }
            )
        if entitlements:
            return self.env["g2p.entitlement"].create(entitlements)
        return None

    def set_pending_validation_entitlements(self, cycle):
        """Set entitlements to pending validation.
        Default Entitlement Manager :meth:`set_pending_validation_entitlements`
        Set entitlements to pending_validation in a cycle

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
        """Set entitlements to pending validation.
        Default Entitlement Manager :meth:`_set_pending_validation_entitlements`
        Synchronous setting of entitlements to pending_validation in a cycle

        :param entitlements: A recordset of entitlements
        :return:
        """
        entitlements.update({"state": "pending_validation"})

    def validate_entitlements(self, cycle):
        """Validate entitlements.
        Default Entitlement Manager :meth:`validate_entitlements`
        Validate entitlements in a cycle

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
            err, message = self._validate_entitlements(entitlements)
            if err > 0:
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Entitlement"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }
            else:
                kind = "success"
                approved_entitlements_count = len(entitlements) - err  # Calculate the approved count
                if err != 0:
                    message = _(
                        f"{approved_entitlements_count} Entitlements are successfully approved and"
                        f"{err} are not approved."
                    )
                else:
                    message = _(f"{approved_entitlements_count} Entitlements are successfully approved.")

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
            self._validate_entitlements_async(cycle, entitlements, entitlements_count)

    def _validate_entitlements(self, entitlements):
        """Validate entitlements.
        Default Entitlement Manager :meth:`_validate_entitlements`
        Synchronous validation of entitlements in a cycle

        :param entitlements: A recordset of entitlements to validate
        :return err: Integer number of errors
        :return message: String description of the error
        """
        err, message = self.approve_entitlements(entitlements)
        return err, message

    def cancel_entitlements(self, cycle):
        """
        Default Entitlement Manager :meth:`cancel_entitlements`
        Cancel entitlements in a cycle

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
        """
        Default Entitlement Manager :meth:`_cancel_entitlements`
        Synchronous cancellation of entitlements in a cycle

        :param entitlements: A recordset of entitlements to cancel
        :return:
        """
        entitlements.update({"state": "cancelled"})

    def _calculate_amount(self, beneficiary, num_individuals):
        total = self.amount_per_cycle
        if beneficiary.is_group:
            if num_individuals:
                if self.max_individual_in_group:
                    num_individuals = min(num_individuals, self.max_individual_in_group)

                total += self.amount_per_individual_in_group * float(num_individuals)
        return total

    def approve_entitlements(self, entitlements):
        """Approve entitlements.
        Default Entitlement Manager :meth:`approve_entitlements`
        Approve selected entitlements

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
        # self.ensure_one()
        action = {
            "name": _("Cycle Entitlements"),
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
            "name": "Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement",
            "res_id": rec.id,
            "view_id": self.env.ref("g2p_programs.view_entitlement_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    @api.model
    def _group_entitlements_by_cycle(self, entitlements):
        cycles = set(map(lambda x: x.cycle_id, entitlements))
        cycle_entitlements = [entitlements.filtered_domain([("cycle_id", "=", cycle.id)]) for cycle in cycles]
        return cycles, cycle_entitlements
