# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from . import constants


class G2PProgramMembership(models.Model):
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    _name = "g2p.program_membership"
    _description = "Program Membership"
    _inherits = {"res.partner": "partner_id"}
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        required=True,
        auto_join=True,
        domain=[("is_registrant", "=", True)],
    )
    program_id = fields.Many2one("g2p.program", "", help="A program", required=True, auto_join=True)

    # TODO: When the state is changed from "exited", "not_eligible" or "duplicate" to something else
    #      then reset the deduplication date.
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("paused", "Paused"),
            ("exited", "Exited"),
            ("not_eligible", "Not Eligible"),
            ("duplicated", "Duplicated"),
        ],
        default="draft",
        copy=False,
    )

    enrollment_date = fields.Datetime(compute="_compute_enrolled_date", store=True)

    last_deduplication = fields.Date("Last Deduplication Date")
    exit_date = fields.Date()

    registrant_id = fields.Integer(string="Registrant ID", related="partner_id.id")

    _sql_constraints = [
        (
            "program_membership_unique",
            "unique (partner_id, program_id)",
            "Beneficiary must be unique per program.",
        ),
    ]

    # TODO: Implement exit reasons
    # exit_reason_id = fields.Many2one("Exit Reason") Default: Completed, Opt-Out, Other

    # TODO: Implement not eligible reasons
    # Default: "Missing data", "Does not match the criterias", "Duplicate", "Other"
    # not_eligible_reason_id = fields.Many2one("Not Eligible Reason")

    # TODO: Add a field delivery_mechanism_id
    # delivery_mechanism_id = fields.Many2one("Delivery mechanism type", help="Delivery mechanism")
    # the phone number, bank account, etc.
    delivery_mechanism_value = fields.Char()

    # TODO: JJ - Add a field for the preferred notification method

    deduplication_status = fields.Selection(
        selection=[
            ("new", "New"),
            ("processing", "Processing"),
            ("verified", "Verified"),
            ("duplicated", "duplicated"),
        ],
        default="new",
        copy=False,
    )

    @api.depends("state")
    def _compute_enrolled_date(self):
        for rec in self:
            if rec.state == "enrolled":
                rec.enrollment_date = fields.Datetime.now()

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        context = self.env.context
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type == "form":
            update_arch = False
            doc = arch
            # Check if we need to change the partner_id domain filter
            target_type = context.get("target_type", False)
            if target_type:
                domain = None
                if context.get("target_type", False) == "group":
                    domain = "[('is_registrant', '=', True), ('is_group','=',True)]"
                elif context.get("target_type", False) == "individual":
                    domain = "[('is_registrant', '=', True), ('is_group','=',False)]"
                if domain:
                    update_arch = True
                    nodes = doc.xpath("//field[@name='partner_id']")
                    for node in nodes:
                        node.set("domain", domain)

            if update_arch:
                arch = etree.tostring(doc, encoding="unicode")
        return arch, view

    def name_get(self):
        res = super().name_get()
        for rec in self:
            name = ""
            if rec.program_id:
                name += "[" + rec.program_id.name + "] "
            if rec.partner_id:
                name += rec.partner_id.name
            rec.display_name = name
        return res

    def open_beneficiaries_form(self):
        for rec in self:
            return {
                "name": "Program Beneficiaries",
                "view_mode": "form",
                "res_model": "g2p.program_membership",
                "res_id": rec.id,
                "view_id": self.env.ref("g2p_programs.view_program_membership_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    "target_type": rec.program_id.target_type,
                    "default_program_id": rec.program_id.id,
                },
            }

    def open_registrant_form(self):
        if self.partner_id.is_group:
            return {
                "name": "Group Member",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
                "view_id": self.env.ref("g2p_registry_group.view_groups_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {"default_is_group": True},
                "flags": {"mode": "readonly"},
            }
        else:
            return {
                "name": "Individual Member",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
                "view_id": self.env.ref("g2p_registry_individual.view_individuals_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {"default_is_group": False},
                "flags": {"mode": "readonly"},
            }

    def verify_eligibility(self):
        eligibility_managers = self.program_id.get_managers(constants.MANAGER_ELIGIBILITY)
        member = self
        for em in eligibility_managers:
            member = em.enroll_eligible_registrants(member)
        if len(member) == 0:
            self.state = "not_eligible"
        return

    def enroll_eligible_registrants(self):
        eligibility_managers = self.program_id.get_managers(constants.MANAGER_ELIGIBILITY)
        message = None
        kind = "success"
        member = self
        for em in eligibility_managers:
            member = em.enroll_eligible_registrants(member)

        if len(member) > 0:
            if self.state != "enrolled":
                self.write(
                    {
                        "state": "enrolled",
                        "enrollment_date": fields.Datetime.now(),
                    }
                )
                message = _("%s Beneficiaries enrolled.", len(member))
                kind = "success"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Enrollment"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

        else:
            self.state = "not_eligible"
            message = "beneficiary is not eligible"
            kind = "warning"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Enrollment"),
                    "message": message,
                    "sticky": False,
                    "type": kind,
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

    def deduplicate_beneficiaries(self):
        deduplication_managers = self.program_id.get_managers(constants.MANAGER_DEDUPLICATION)

        message = None
        kind = "success"
        if len(deduplication_managers):
            states = ["draft", "enrolled", "eligible", "paused", "duplicated"]
            duplicates = 0
            for el in deduplication_managers:
                duplicates += el.deduplicate_beneficiaries(states)

                if duplicates > 0:
                    message = _("%s Beneficiaries duplicate.", duplicates)
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

    def Back_to_draft(self):
        self.write(
            {
                "state": "draft",
            }
        )
        return
