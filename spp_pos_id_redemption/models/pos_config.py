from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    area_id = fields.Many2one("spp.area", string="Area")
