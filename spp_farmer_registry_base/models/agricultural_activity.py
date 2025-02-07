from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    species_id = fields.Many2one(
        "spp.farm.species", ondelete="restrict", string="Species", domain="[('species_type', '=', activity_type)]"
    )

    season_id = fields.Many2one(
        "spp.farm.season",
        string="Agricultural Season",
        domain="[('state', '=', 'active')]",
    )

    @api.onchange("crop_farm_id")
    def _onchange_farm_id(self):
        for rec in self:
            rec.land_id = False

    @api.constrains("season_id")
    def _check_season_state(self):
        for record in self:
            if record.season_id and record.season_id.state == "closed":
                raise ValidationError(_("Cannot modify activities in closed seasons"))

    @api.model
    def default_get(self, fields_list):
        """Set default season to most recent active season"""
        res = super().default_get(fields_list)
        if "season_id" in fields_list:
            active_season = self.env["spp.farm.season"].search(
                [("state", "=", "active")], order="date_start desc", limit=1
            )
            if active_season:
                res["season_id"] = active_season.id
        return res

    def write(self, vals):
        """Prevent modifications in closed seasons"""
        for record in self:
            if record.season_id and record.season_id.state == "closed":
                raise ValidationError(_("Cannot modify activities in closed seasons"))
        return super().write(vals)
