from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    longitude = fields.Text()
    latitude = fields.Text()
