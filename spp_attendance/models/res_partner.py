from odoo import fields, models


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    family_name = fields.Char(translate=False)
    given_name = fields.Char(translate=False)
    addl_name = fields.Char(translate=False, string="Additional Name")
    identifier = fields.Char()
    gender = fields.Char(translate=False, default="Male")
