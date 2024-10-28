from odoo import fields, models


class Farm(models.Model):
    _inherit = "res.partner"

    household_size = fields.Integer()
