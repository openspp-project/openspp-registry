from odoo import fields, models


class CustomG2PCycleMembership(models.Model):
    _inherit = "g2p.cycle.membership"

    # Use only this field for group registrant
    cycle_group_membership_attendance_ids = fields.One2many(
        "spp.cycle.group.membership.attendance",
        "cycle_membership_id",
        "Cycle Group Membership Attendance",
    )

    partner_is_group = fields.Boolean(
        related="partner_id.is_group",
        string="Partner is Group",
        readonly=True,
    )

    allow_filter_compliance_criteria = fields.Boolean(
        related="cycle_id.allow_filter_compliance_criteria",
    )

    number_of_attendance = fields.Integer("Number of Attendance", default=0)
