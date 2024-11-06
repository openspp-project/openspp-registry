from odoo import fields, models


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    family_name = fields.Char(translate=False)
    given_name = fields.Char(translate=False)
    identifier = fields.Char()
