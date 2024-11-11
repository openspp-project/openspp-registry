from odoo import api, fields, models


class AgriculturalActivity(models.Model):
    _name = "spp.farm.activity"
    _description = "Agricultural Activities"

    crop_farm_id = fields.Many2one("res.partner", string="Crop Farm")
    live_farm_id = fields.Many2one("res.partner", string="Livestock Farm")
    aqua_farm_id = fields.Many2one("res.partner", string="Aqua Farm")
    land_id = fields.Many2one(
        "spp.land.record",
        string="Land",
        required=False,
        domain="[('farm_id', '=', farm_id)]",
    )

    purpose = fields.Selection(
        [
            ("subsistence", "Subsistence"),
            ("commercial", "Commercial"),
            ("both", "Both"),
        ],
    )

    activity_type = fields.Selection(
        [
            ("crop", "Crop Cultivation"),
            ("livestock", "Livestock Rearing"),
            ("aquaculture", "Aquaculture"),
        ],
    )

    species_id = fields.Many2one("spp.farm.species", string="Species", domain="[('species_type', '=', activity_type)]")

    @api.onchange("crop_farm_id")
    def _onchange_farm_id(self):
        for rec in self:
            rec.land_id = False
