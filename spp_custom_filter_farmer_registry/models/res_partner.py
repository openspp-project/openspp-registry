from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "custom.filter.mixin"]

    farmer_national_id = fields.Char(allow_filter=True)
    farmer_postal_address = fields.Char(allow_filter=True)
    marital_status = fields.Selection(allow_filter=True)
    highest_education_level = fields.Selection(allow_filter=True)
