from odoo import fields, models


class G2PGroupMembership(models.Model):
    _inherit = "g2p.group.membership"

    individual_gender = fields.Many2one("gender.type", related="individual.gender", readonly=True)
