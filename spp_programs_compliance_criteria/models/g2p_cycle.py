from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import OR


class G2pCycle(models.Model):
    _inherit = "g2p.cycle"

    allow_filter_compliance_criteria = fields.Boolean(compute="_compute_allow_filter_compliance_criteria")
    all_members_count = fields.Integer(string="# Enrollments", readonly=True, compute="_compute_all_members_count")

    @api.depends("program_id", "program_id.compliance_managers")
    def _compute_allow_filter_compliance_criteria(self):
        for rec in self:
            rec.allow_filter_compliance_criteria = bool(rec.program_id.compliance_managers)

    def action_filter_beneficiaries_by_compliance_criteria(self):
        self.ensure_one()
        if not self.program_id.compliance_managers:
            raise ValidationError(_("Cycle is not on correct condition to filter by compliance!"))
        if self.state not in ("draft", "to_approve") or not self.cycle_membership_ids:
            return
        registrant_satisfied = self.env["res.partner"].sudo().search(self._get_compliance_criteria_domain())
        membership_to_paused = self.cycle_membership_ids.filtered(lambda cm: cm.partner_id not in registrant_satisfied)
        membership_to_paused.state = "paused"
        membership_to_enrolled = self.cycle_membership_ids - membership_to_paused
        membership_to_enrolled.state = "enrolled"

    def _get_compliance_criteria_domain(self):
        self.ensure_one()
        domain = []
        for manager in self.program_id.compliance_managers:
            manager_ref = manager.manager_ref_id
            if manager_ref._name == "g2p.program_membership.manager.sql":
                domain.append([("id", "in", manager_ref._get_beneficiaries_sql_query())])
                continue
            membership = self.cycle_membership_ids if self.cycle_membership_ids else None
            domain.append(manager_ref._prepare_eligible_domain(membership))
        return OR(domain)

    def _compute_all_members_count(self):
        for rec in self:
            domain = rec._get_beneficiaries_domain(None)
            members_count = self.env["g2p.cycle.membership"].search_count(domain)
            rec.update({"all_members_count": members_count})

    def open_all_members_form(self):
        self.ensure_one()

        action = {
            "name": _("Cycle Members"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.cycle.membership",
            "context": {
                "create": False,
                "default_cycle_id": self.id,
            },
            "view_mode": "list,form",
            "domain": [("cycle_id", "=", self.id)],
        }
        return action

    def open_members_form(self):
        self.ensure_one()
        action = super().open_members_form()
        action["name"] = _("Cycle Beneficiaries")
        return action
