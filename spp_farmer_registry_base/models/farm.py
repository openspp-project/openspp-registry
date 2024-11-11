import json
import logging

import pyproj
from shapely.geometry import mapping
from shapely.ops import transform

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Farm(models.Model):
    _inherit = "res.partner"
    _inherits = {
        "spp.land.record": "farm_land_rec_id",
        "spp.farm.details": "farm_detail_id",
        "spp.farmer": "farmer_id",
    }

    coordinates = fields.GeoPointField(string="GPS Coordinates")
    farm_asset_ids = fields.One2many("spp.farm.asset", "asset_farm_id", string="Farm Assets")
    farm_machinery_ids = fields.One2many("spp.farm.asset", "machinery_farm_id", string="Farm Machinery")
    farm_details_ids = fields.One2many("spp.farm.details", "details_farm_id", string="Farm Details")
    farm_land_rec_ids = fields.One2many("spp.land.record", "land_farm_id", string="Land Records")

    farm_extension_ids = fields.One2many("spp.farm.extension", "farm_id", string="Farm Extension Services")
    farm_crop_act_ids = fields.One2many("spp.farm.activity", "crop_farm_id", string="Crop Agricultural Activities")
    farm_live_act_ids = fields.One2many("spp.farm.activity", "live_farm_id", string="Livestock Agricultural Activities")
    farm_aqua_act_ids = fields.One2many(
        "spp.farm.activity",
        "aqua_farm_id",
        string="Aquaculture Agricultural Activities",
    )

    farm_asset_id = fields.Many2one("spp.farm.asset", string="Farm Asset")
    farm_detail_id = fields.Many2one("spp.farm.details", required=True, ondelete="cascade", string="Farm Detail")
    farm_land_rec_id = fields.Many2one("spp.land.record", required=True, ondelete="cascade", string="Land Record")
    farmer_id = fields.Many2one("spp.farmer", required=True, ondelete="cascade", string="Farmer")

    @api.model_create_multi
    def create(self, vals):
        farm = super().create(vals)
        if farm.is_group:
            self.create_update_farmer(farm)
        elif not farm.is_group and farm.is_registrant:
            self.update_farmer(farm)

        return farm

    def get_group_head_member(self):
        self.ensure_one()
        if not self.is_registrant or not self.is_group:
            return None

        head_kind_id = self.env.ref("g2p_registry_membership.group_membership_kind_head")
        for member in self.group_membership_ids:
            if head_kind_id in member.kind:
                return member.individual

    def update_group_head_member(self, new_group_head):
        self.ensure_one()
        current_phone = self.env["g2p.phone.number"].search([("partner_id", "=", new_group_head.id)], limit=1)
        phone_number = None
        if current_phone:
            phone_number = current_phone.phone_no

        current_id = self.env["g2p.reg.id"].search(
            [
                ("partner_id", "=", new_group_head.id),
                (
                    "id_type",
                    "=",
                    self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                ),
            ]
        )
        national_id = None
        if current_id:
            national_id = current_id.value

        self.farmer_id.write(
            {
                "farmer_individual_id": new_group_head.id,
                "farmer_family_name": new_group_head.family_name,
                "farmer_given_name": new_group_head.given_name,
                "farmer_addtnl_name": new_group_head.addl_name,
                "farmer_sex": new_group_head.gender,
                "farmer_marital_status": new_group_head.marital_status,
                "farmer_birthdate": new_group_head.birthdate,
                "farmer_household_size": new_group_head.farmer_household_size,
                "farmer_postal_address": new_group_head.farmer_postal_address,
                "farmer_email": new_group_head.email,
                "farmer_formal_agricultural": new_group_head.formal_agricultural_training,
                "farmer_highest_education_level": new_group_head.highest_education_level,
                "farmer_national_id": national_id,
                "farmer_mobile_tel": phone_number,
            }
        )
        self.write(
            {
                "farmer_national_id": national_id,
                "farmer_household_size": new_group_head.farmer_household_size,
                "farmer_postal_address": new_group_head.farmer_postal_address,
            }
        )
        new_group_head.farmer_id = self.farmer_id.id

    @api.model
    def write(self, vals):
        farm = super().write(vals)

        self._create_update_farmer()

        return farm

    def _create_update_farmer(self):
        for rec in self:
            if rec.is_group:
                head_member = rec.get_group_head_member()
                if not head_member:
                    raise ValidationError(_("Farm must have a head member."))
                if head_member and head_member.id != rec.farmer_individual_id.id:
                    rec.update_group_head_member(head_member)
                    continue

                rec.create_update_farmer(rec)
            elif not rec.is_group and rec.is_registrant:
                rec.update_farmer(rec)

    def _process_record_to_feature(self, record, transformer):
        """
        Convert a farm record to a GeoJSON feature using shapely and geojson libraries.

        Args:
            record: The farm record to process.

        Returns:
            A GeoJSON feature dictionary or None if coordinates are not found.
        """
        if not record.coordinates:
            return None  # Skip records without coordinates

        point_transformed = mapping(transform(transformer, record.coordinates))

        # Construct the feature with the geometry and properties
        feature = {
            "type": "Feature",
            "geometry": point_transformed,
            "properties": {
                "name": record.name,  # Include any other properties you want in the GeoJSON
            },
        }

        return feature

    @api.model
    def get_geojson(self):
        """
        Generate a GeoJSON representation of farm records.

        Returns:
            A GeoJSON string of farm records.
        """
        # Query all farms with coordinates
        # farms = self.search([('coordinates', '!=', False)])
        farms = self.search([])

        # Construct GeoJSON structure
        geojson_features = {"type": "FeatureCollection", "features": []}

        # Assuming coordinates are in EPSG:3857 (Pseudo-Mercator)
        proj_from = pyproj.Proj("epsg:3857")  # EPSG:3857 - WGS 84 / Pseudo-Mercator
        proj_to = pyproj.Proj("epsg:4326")  # WGS84
        transformer = pyproj.Transformer.from_proj(proj_from, proj_to, always_xy=True).transform

        for farm in farms:
            feature = self._process_record_to_feature(farm, transformer)
            if feature:
                geojson_features["features"].append(feature)

        return json.dumps(geojson_features, indent=2)

    def create_update_farmer(self, farm):
        farmer_name = ""
        if farm.farmer_family_name:
            farmer_name += farm.farmer_family_name + ", "
        if farm.farmer_given_name:
            farmer_name += farm.farmer_given_name + " "
        if farm.farmer_addtnl_name:
            farmer_name += farm.farmer_addtnl_name

        individual_vals = {
            "family_name": farm.farmer_family_name,
            "given_name": farm.farmer_given_name,
            "name": farmer_name,
            "addl_name": farm.farmer_addtnl_name or None,
            "farmer_national_id": farm.farmer_national_id or None,
            "gender": farm.farmer_sex or None,
            "marital_status": farm.farmer_marital_status or None,
            "birthdate": farm.farmer_birthdate or None,
            "farmer_household_size": farm.farmer_household_size or None,
            "farmer_postal_address": farm.farmer_postal_address or None,
            "email": farm.farmer_email or None,
            "formal_agricultural_training": farm.farmer_formal_agricultural or None,
            "highest_education_level": farm.farmer_highest_education_level or None,
            "is_registrant": True,
            "is_group": False,
        }
        if not farm.farmer_individual_id:
            individual = self.env["res.partner"].create(individual_vals)
            # Create Membership
            membership_vals = {
                "group": farm.id,
                "individual": individual.id,
                "kind": [Command.link(self.env.ref("g2p_registry_membership.group_membership_kind_head").id)],
            }
            self.env["g2p.group.membership"].create(membership_vals)
            individual.farmer_id = farm.farmer_id.id
            farm.farmer_individual_id = individual.id
            self.insert_phone_number(farm.farmer_individual_id.id, farm.farmer_mobile_tel)
            self.insert_id(farm.farmer_individual_id.id, farm.farmer_national_id)

        else:
            self.insert_phone_number(farm.farmer_individual_id.id, farm.farmer_mobile_tel)
            self.insert_id(farm.farmer_individual_id.id, farm.farmer_national_id)
            farm.farmer_individual_id.write(individual_vals)

    def insert_phone_number(self, individual_id, mobile_no):
        if mobile_no:
            current_phone = self.env["g2p.phone.number"].search([("partner_id", "=", individual_id)], limit=1)
            if not current_phone:
                individual_phone_vals = {"partner_id": individual_id, "phone_no": mobile_no}
                self.env["g2p.phone.number"].create(individual_phone_vals)
            else:
                current_phone.write({"phone_no": mobile_no})

    def insert_id(self, individual_id, national_id):
        if national_id:
            current_id = self.env["g2p.reg.id"].search(
                [
                    ("partner_id", "=", individual_id),
                    ("value", "=", national_id),
                    (
                        "id_type",
                        "=",
                        self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                    ),
                ]
            )
            if not current_id:
                existing_national_id = self.env["g2p.reg.id"].search(
                    [
                        ("partner_id", "=", individual_id),
                        (
                            "id_type",
                            "=",
                            self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                        ),
                    ]
                )
                id_vals = {
                    "partner_id": individual_id,
                    "value": national_id,
                    "id_type": self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                }
                if existing_national_id:
                    existing_national_id.write(id_vals)
                else:
                    self.env["g2p.reg.id"].create(id_vals)

    def update_farmer(self, individual):
        farmer_vals = {
            "farmer_family_name": individual.family_name,
            "farmer_given_name": individual.given_name,
            "farmer_addtnl_name": individual.addl_name or None,
            "farmer_sex": individual.gender or None,
            "farmer_marital_status": individual.marital_status or None,
            "farmer_birthdate": individual.birthdate or None,
            "farmer_household_size": individual.farmer_household_size or None,
            "farmer_postal_address": individual.farmer_postal_address or None,
            "farmer_email": individual.email or None,
            "farmer_formal_agricultural": individual.formal_agricultural_training or None,
            "farmer_highest_education_level": individual.highest_education_level or None,
        }
        farmer_national_id = self.env["g2p.reg.id"].search(
            [
                ("partner_id", "=", individual.id),
                (
                    "id_type",
                    "=",
                    self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                ),
            ],
            limit=1,
        )
        if farmer_national_id:
            farmer_vals.update({"farmer_national_id": farmer_national_id.value or None})

        farmer_phone = self.env["g2p.phone.number"].search(
            [
                ("partner_id", "=", individual.id),
            ],
            limit=1,
        )
        if farmer_phone:
            farmer_vals.update({"farmer_mobile_tel": farmer_phone.phone_no or None})

        if farmer_vals:
            individual.farmer_id.write(farmer_vals)
