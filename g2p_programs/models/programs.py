# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from . import constants

_logger = logging.getLogger(__name__)


class G2PProgram(models.Model):
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "job.relate.mixin",
        # "disable.edit.mixin",
    ]
    _name = "g2p.program"
    _description = "Program"
    _order = "id desc"
    _check_company_auto = True

    MANAGER_ELIGIBILITY = constants.MANAGER_ELIGIBILITY
    MANAGER_CYCLE = constants.MANAGER_CYCLE
    MANAGER_PROGRAM = constants.MANAGER_PROGRAM
    MANAGER_ENTITLEMENT = constants.MANAGER_ENTITLEMENT
    MANAGER_DEDUPLICATION = constants.MANAGER_DEDUPLICATION
    MANAGER_NOTIFICATION = constants.MANAGER_NOTIFICATION
    MANAGER_PAYMENT = constants.MANAGER_PAYMENT

    MANAGER_MODELS = constants.MANAGER_MODELS
    # DISABLE_EDIT_DOMAIN = [("state", "=", "ended")]

    # TODO: Associate a Wallet to each program using the accounting module
    # TODO: (For later) Associate a Warehouse to each program using the stock module for in-kind programs

    @api.model
    def _default_journal_id(self):
        journals = self.env["account.journal"].search(
            [("beneficiary_disb", "=", True), ("type", "in", ("bank", "cash"))]
        )
        if journals:
            return journals[0].id
        else:
            return None

    name = fields.Char(required=True)
    description = fields.Text(string="description")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    target_type = fields.Selection(
        selection=[("group", "Group"), ("individual", "Individual")], default="group"
    )

    # delivery_mechanism = fields.Selection([("mobile", "Mobile"), ("bank_account", "Bank Account"),
    # ("id", "ID Document"), ("biometric", "Biometrics")], default='id')

    # Pre-cycle steps
    # TODO: for those, we should allow to have multiple managers and
    #  the order of the steps should be defined by the user
    eligibility_managers = fields.Many2many("g2p.eligibility.manager")  # All will be run
    deduplication_managers = fields.Many2many("g2p.deduplication.manager")  # All will be run
    # for each beneficiary, their preferred will be used or the first one that works.
    notification_managers = fields.Many2many("g2p.program.notification.manager")
    program_managers = fields.Many2many("g2p.program.manager")
    # Cycle steps
    cycle_managers = fields.Many2many("g2p.cycle.manager")
    entitlement_managers = fields.Many2many("g2p.program.entitlement.manager")
    # Payment management
    payment_managers = fields.Many2many("g2p.program.payment.manager")

    reconciliation_managers = fields.Selection([])

    program_membership_ids = fields.One2many("g2p.program_membership", "program_id", "Program Memberships")
    have_members = fields.Boolean(
        string="Have Beneficiaries",
        compute="_compute_have_members",
        default=False,
        store=True,
    )
    cycle_ids = fields.One2many("g2p.cycle", "program_id", "Cycles")

    date_ended = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("ended", "Ended")],
        "Status",
        default="active",
        readonly=True,
    )

    # Accounting config
    journal_id = fields.Many2one(
        "account.journal",
        "Disbursement Journal",
        domain=[("beneficiary_disb", "=", True), ("type", "in", ("bank", "cash"))],
        default=_default_journal_id,
    )

    # Statistics
    eligible_beneficiaries_count = fields.Integer(
        string="# Eligible Beneficiaries",
        readonly=True,
        compute="_compute_eligible_beneficiary_count",
    )
    beneficiaries_count = fields.Integer(
        string="# Beneficiaries", readonly=True, compute="_compute_beneficiary_count"
    )

    cycles_count = fields.Integer(string="# Cycles", compute="_compute_cycle_count", store=True)
    duplicate_membership_count = fields.Integer(
        string="# Membership Duplicates", compute="_compute_duplicate_membership_count"
    )
    active = fields.Boolean(default=True)

    # This is used to prevent any issue while some background tasks are happening
    #  such as importing beneficiaries
    locked = fields.Boolean(default=False)
    locked_reason = fields.Char()

    def toggle_active(self):
        """
        Overrides the default :meth:`toggle_active` to cancel
        all `draft`, `to_approve`, and `approved` associated cycles and
        'draft' and 'pending_validation' entitlements.

        :return: toggle_active function of parent class
        """
        for rec in self:
            # Cancel cycles and entitlements only if the program is active (for archiving)
            if rec.active:
                _logger.debug("Archive Program: cancel cycles and entitlements.")
                if rec.cycle_ids:
                    entitlement_manager = rec.get_manager(self.MANAGER_ENTITLEMENT)
                    # Get only `draft`, `to_approve`, and `approved` cycles
                    cycles = rec.cycle_ids.filtered(lambda a: a.state in ("draft", "to_approve", "approved"))
                    if cycles:
                        for cycle in cycles:
                            entitlement_manager.cancel_entitlements(cycle)
                        # Set the cycle_ids state to 'cancelled'
                        cycles.update({"state": "cancelled"})
        return super().toggle_active()

    @api.depends("program_membership_ids")
    def _compute_have_members(self):
        if len(self.program_membership_ids) > 0:
            self.have_members = True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        program_id = res.id
        man_ids = self.create_default_managers(program_id)
        for man in man_ids:
            res.update({man: [(4, man_ids[man])]})
        return res

    @api.model
    def create_default_managers(self, program_id):
        ret_vals = {}
        for mgr_fld in self.MANAGER_MODELS:
            for mgr_obj in self.MANAGER_MODELS[mgr_fld]:
                # Add a new record to default manager models
                def_mgr_obj = self.MANAGER_MODELS[mgr_fld][mgr_obj]
                _logger.debug("DEBUG: %s" % def_mgr_obj)
                def_mgr = self.env[def_mgr_obj].create(
                    {
                        "name": "Default",
                        "program_id": program_id,
                    }
                )
                # Add a new record to manager parent models
                man_obj = self.env[mgr_obj]
                mgr = man_obj.create(
                    {
                        "program_id": program_id,
                        "manager_ref_id": f"{def_mgr_obj},{str(def_mgr.id)}",
                    }
                )
                ret_vals.update({mgr_fld: mgr.id})
        return ret_vals

    def _compute_duplicate_membership_count(self):
        for rec in self:
            count = rec.count_beneficiaries(["duplicated"])["value"]
            rec.update({"duplicate_membership_count": count})

    def _compute_eligible_beneficiary_count(self):
        for rec in self:
            count = rec.count_beneficiaries(["enrolled"])["value"]
            rec.update({"eligible_beneficiaries_count": count})

    def _compute_beneficiary_count(self):
        for rec in self:
            count = rec.count_beneficiaries(None)["value"]
            rec.update({"beneficiaries_count": count})

    @api.depends("cycle_ids")
    def _compute_cycle_count(self):
        for rec in self:
            domain = [("program_id", "=", rec.id)]
            count = self.env["g2p.cycle"].search_count(domain)
            rec.update({"cycles_count": count})

    @api.model
    def get_manager(self, kind):
        self.ensure_one()
        for rec in self:
            if kind == self.MANAGER_CYCLE:
                managers = rec.cycle_managers
            elif kind == self.MANAGER_PROGRAM:
                managers = rec.program_managers
            elif kind == self.MANAGER_ENTITLEMENT:
                managers = rec.entitlement_managers
            elif kind == self.MANAGER_PAYMENT:
                managers = rec.payment_managers
            else:
                raise NotImplementedError("Manager not supported")
            if managers:
                managers.ensure_one()
                for el in managers:
                    return el.manager_ref_id

    @api.model
    def get_managers(self, kind):
        self.ensure_one()
        for rec in self:
            if kind == self.MANAGER_ELIGIBILITY:
                managers = rec.eligibility_managers
            elif kind == self.MANAGER_DEDUPLICATION:
                managers = rec.deduplication_managers
            elif kind == self.MANAGER_NOTIFICATION:
                managers = rec.notification_managers
            else:
                raise NotImplementedError("Manager not supported")
            return [el.manager_ref_id for el in managers]

    @api.model
    def get_beneficiaries(self, state=None, offset=0, limit=None, order=None, count=False):
        self.ensure_one()
        if isinstance(state, str):
            state = [state]
        domain = [("program_id", "=", self.id)]
        if state is not None:
            domain.append(("state", "in", state))
        if count:
            return self.env["g2p.program_membership"].search_count(domain, limit=limit)

        return self.env["g2p.program_membership"].search(domain, offset=offset, limit=limit, order=order)

    # TODO: JJ - Review
    def count_beneficiaries(self, state=None):
        domain = [("program_id", "=", self.id)]
        if state is not None:
            domain += [("state", "in", state)]

        return {"value": self.env["g2p.program_membership"].search_count(domain)}

    # TODO: JJ - Add a way to link reports/Dashboard about this program.

    def enroll_eligible_registrants(self):
        if self.beneficiaries_count <= 0:
            raise UserError(_("No Registrants Added to Program"))
        for rec in self:
            program_manager = rec.get_manager(self.MANAGER_PROGRAM)
            if program_manager:
                return program_manager.enroll_eligible_registrants()
            else:
                raise UserError(_("No Program Manager defined."))

    def verify_eligibility(self):
        for rec in self:
            program_manager = rec.get_manager(self.MANAGER_PROGRAM)
            if program_manager:
                return program_manager.enroll_eligible_registrants(["enrolled", "not_eligible"])

            else:
                raise UserError(_("No Program Manager defined."))

    def deduplicate_beneficiaries(self):
        for rec in self:
            deduplication_managers = rec.get_managers(self.MANAGER_DEDUPLICATION)
            message = None
            kind = "success"
            if len(deduplication_managers):
                states = ["draft", "enrolled", "eligible", "paused", "duplicated"]
                duplicates = 0
                for el in deduplication_managers:
                    duplicates += el.deduplicate_beneficiaries(states)

                if duplicates > 0:
                    message = _("%s Instances of Beneficiaries duplicate.", duplicates)
                    kind = "warning"
                else:
                    message = _("No duplicates found.")
                    kind = "success"
            else:
                raise UserError(_("No Deduplication Manager defined."))

            if message:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Deduplication"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

    def notify_eligible_beneficiaries(self):
        # 1. Notify the beneficiaries using notification_manager.enrolled_in_program()
        pass

    def create_new_cycle(self):
        # 1. Create the next cycle using cycles_manager.new_cycle()
        # 2. Import the beneficiaries from the previous cycle to this one.
        #  If it is the first one, import from the
        # program memberships.
        if self.beneficiaries_count <= 0:
            raise UserError(_("No enrolled registrants. Enroll registrants to program to create new cycle."))
        for rec in self:
            message = None
            kind = "success"
            cycle_manager = rec.get_manager(self.MANAGER_CYCLE)
            program_manager = rec.get_manager(self.MANAGER_PROGRAM)
            if cycle_manager is None:
                raise UserError(_("No Cycle Manager defined."))
            elif program_manager is None:
                raise UserError(_("No Program Manager defined."))
            if message is not None:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Cycle"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

            _logger.debug("-" * 80)
            _logger.debug("pm: %s", program_manager)
            new_cycle = program_manager.new_cycle()
            message = _("New cycle %s created.", new_cycle.name)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Cycle"),
                    "message": message,
                    "sticky": False,
                    "type": kind,
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

    def create_journal(self):
        for rec in self:
            program_name = rec.name.split(" ")
            code = ""
            for pn in program_name:
                if pn:
                    code += pn[0].upper()
            if len(code) == 0:
                code = program_name[3].strip().upper()
            account_chart = self.env["account.account"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("account_type", "=", "asset_cash"),
                ]
            )
            default_account_id = None
            if account_chart:
                default_account_id = account_chart[0].id
            new_journal = self.env["account.journal"].create(
                {
                    "name": rec.name,
                    "beneficiary_disb": True,
                    "type": "bank",
                    "default_account_id": default_account_id,
                    "code": code,
                    "currency_id": rec.company_id.currency_id and rec.company_id.currency_id.id or None,
                }
            )
            rec.update({"journal_id": new_journal.id})

    def end_program(self):
        for rec in self.env.context.get("active_ids"):
            program = self.env["g2p.program"].search(
                [
                    ("id", "=", rec),
                ]
            )
            if program.state == "active":
                program.update({"state": "ended", "date_ended": fields.Date.today()})
            else:
                message = _("Ony 'active' programs can be ended.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Program"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

    def reactivate_program(self):
        for rec in self.env.context.get("active_ids"):
            program = self.env["g2p.program"].search(
                [
                    ("id", "=", rec),
                ]
            )
            if program.state == "ended":
                program.update({"state": "active", "date_ended": None})
            else:
                message = _("Ony 'ended' programs can be re-activated.")
                kind = "danger"

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Project"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

    def open_eligible_beneficiaries_form(self):
        self.ensure_one()

        action = {
            "name": _("Beneficiaries"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.program_membership",
            "context": {
                "create": False,
                "default_program_id": self.id,
                # "search_default_enrolled_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id)],
        }
        return action

    def open_duplicate_membership_form(self):
        self.ensure_one()

        action = {
            "name": _("Beneficiaries Duplicates"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.program_membership",
            "context": {
                "create": False,
                "default_program_id": self.id,
                # "search_default_enrolled_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id), ("state", "=", "duplicated")],
        }
        return action

    def open_cycles_form(self):
        self.ensure_one()

        action = {
            "name": _("Cycles"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.cycle",
            "context": {
                "create": False,
                "default_program_id": self.id,
                # "search_default_approved_state": 1,
                # "search_default_to_approve_state": 1,
            },
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id)],
        }
        return action

    def refresh_page(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def _get_related_job_domain(self):
        jobs = self.env["queue.job"].search([("model_name", "like", self._name)])
        related_jobs = jobs.filtered(lambda r: self in r.records.program_id)
        return [("id", "in", related_jobs.ids)]

    @api.constrains("entitlement_managers", "program_managers", "cycle_managers", "payment_managers")
    def check_managers_limit(self):
        for record in self:
            error_messages = []

            if len(record.entitlement_managers) > 1:
                error_messages.append("Entitlement Managers")

            if len(record.program_managers) > 1:
                error_messages.append("Program Managers")

            if len(record.cycle_managers) > 1:
                error_messages.append("Cycle Managers")

            if len(record.payment_managers) > 1:
                error_messages.append("Payment Managers")

            if error_messages:
                combined_message = ", ".join(error_messages)
                raise UserError(
                    f"Only one manager can be configured under {combined_message}."
                    f"Please delete any new manager(s) before saving your changes."  # noqa: B950
                )

    def unlink(self):
        managers_to_delete = [
            self.eligibility_managers,
            self.deduplication_managers,
            self.notification_managers,
            self.program_managers,
            self.cycle_managers,
            self.entitlement_managers,
            self.payment_managers,
            self.reconciliation_managers,
        ]

        for managers in managers_to_delete:
            if managers:
                for manager in managers:
                    manager.manager_ref_id.unlink()
                managers.unlink()
            else:
                return super().unlink()
