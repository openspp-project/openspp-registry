from odoo import fields, models


class OpenSPPArea(models.Model):
    _inherit = "spp.area"

    coordinates = fields.GeoPointField()
    geo_polygon = fields.GeoPolygonField()
