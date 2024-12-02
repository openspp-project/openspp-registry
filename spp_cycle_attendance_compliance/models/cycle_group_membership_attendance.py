from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SPPCycleGroupMembershipAttendance(models.Model):
    _name = "spp.cycle.group.membership.attendance"
    _description = "Cycle Group Membership Attendance"

    cycle_membership_id = fields.Many2one("g2p.cycle.membership", "Cycle Membership", required=True)
    individual_id = fields.Many2one(
        "res.partner", "Individual", required=True, domain="[('is_group', '=', False), ('is_registrant', '=', True)]"
    )
    number_of_attendance_str = fields.Char("Number of Attendance", required=True, default="0")
    state = fields.Selection(
        selection=[
            ("included", "Included"),
            ("not_included", "Not Included"),
        ],
        default="included",
    )

    @api.constrains("number_of_attendance_str")
    def _check_number_of_attendance_str(self):
        for rec in self:
            try:
                int(rec.number_of_attendance_str)
            except Exception as e:
                raise ValidationError(_("Number of Attendance must be a number.")) from e

    def open_members_form(self):
        return {
            "name": "Cycle Group Members",
            "view_mode": "form",
            "res_model": "res.partner",
            "res_id": self.individual_id.id,
            "view_id": self.env.ref("g2p_registry_individual.view_individuals_form").id,
            "type": "ir.actions.act_window",
            "target": "current",
            "flags": {"mode": "readonly"},
        }
