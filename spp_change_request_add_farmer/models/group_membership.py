from odoo import fields, models


class SPPGroupMembership(models.Model):
    _inherit = "spp.change.request.group.members"

    group_add_farmer_id = fields.Many2one("spp.change.request.add.farmer")
    individual_id = fields.Many2one(
        "res.partner",
        string="Registrant",
        domain="[('is_group', '=', False),('is_registrant', '=', True),('individual_membership_ids', '=', False)]",
    )
