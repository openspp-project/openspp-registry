import json

import pyproj
from shapely.geometry import mapping
from shapely.ops import transform

from odoo import api, fields, models


class LandRecord(models.Model):
    _name = "spp.land.record"
    _description = "Land Record Details"
    _record_name = "land_name"

    land_farm_id = fields.Many2one("res.partner", string="Farm")
    land_name = fields.Char(string="Parcel Name/ID")
    land_acreage = fields.Float()

    # TODO: Change to geo_point and geo_polygon
    land_coordinates = fields.GeoPointField()
    land_geo_polygon = fields.GeoPolygonField(string="Land Polygons")

    land_use = fields.Selection(
        [
            ("cultivation", "Cultivation"),
            ("livestock", "Livestock"),
            ("aquaculture", "Aquaculture"),
            ("mixed", "Mixed Use"),
            ("fallow", "Fallow"),
            ("leased_out", "Leased Out"),
            ("other", "Other"),
        ],
    )

    owner_id = fields.Many2one("res.partner")
    lessee_id = fields.Many2one("res.partner")

    lease_start = fields.Date()
    lease_end = fields.Date()

    def _process_record_to_feature(self, record, geometry_type, transformer):
        """
        Convert a record to a GeoJSON feature using shapely and geojson libraries.

        Args:
            record: The record to process.
            geometry_type: The type of geometry to process ('point', 'polygon', or 'all').
            transformer: The transformer to use for the projection.

        Returns:
            A GeoJSON feature dictionary or None if no valid geometry found.
        """
        # Initialize the feature dictionary with properties
        feature = {
            "type": "Feature",
            "properties": {
                "land_name": record.land_name,
                "land_use": record.land_use,
                "land_acreage": record.land_acreage,
                # Include other properties as needed
            },
        }

        # Process polygon geometry with priority
        if geometry_type in ["polygon", "all"] and record.land_geo_polygon:
            # Assuming land_geo_polygon is a shapely object
            feature["geometry"] = mapping(transform(transformer, record.land_geo_polygon))
        # Fallback to point geometry if requested or no polygon is available
        elif geometry_type in ["point", "all"] and record.land_coordinates:
            feature["geometry"] = mapping(transform(transformer, record.land_coordinates))

        else:
            # No valid geometry found based on the preferences
            return None

        return feature

    @api.model
    def get_geojson(self, geometry_type="all", from_srid=3857, to_srid=4326):
        """
        Generate a GeoJSON representation of land records.

        :param geometry_type: A string specifying the type of geometry to include ('point', 'polygon', or 'all').
        :return: A GeoJSON string of land records.
        """
        search_domain = self._get_search_domain_by_geometry_type(geometry_type)
        land_records = self.search(search_domain)

        # Construct GeoJSON structure
        geojson = {"type": "FeatureCollection", "features": []}

        proj_from = pyproj.Proj(f"epsg:{from_srid}")
        proj_to = pyproj.Proj(f"epsg:{to_srid}")
        transformer = pyproj.Transformer.from_proj(proj_from, proj_to, always_xy=True).transform

        for record in land_records:
            feature = self._process_record_to_feature(record, geometry_type, transformer)
            if feature:
                geojson["features"].append(feature)

        return json.dumps(geojson, indent=2)

    def _get_search_domain_by_geometry_type(self, geometry_type):
        """
        Determine the search domain based on the requested geometry type.

        :param geometry_type: The geometry type ('point', 'polygon', or 'all').
        :return: A search domain for the ORM.
        """
        # if geometry_type == 'point':
        #     return [('land_coordinates', '!=', False)]
        # elif geometry_type == 'polygon':
        #     return [('land_geo_polygon', '!=', False)]
        # else:  # 'all'
        #     return ['|', ('land_coordinates', '!=', False), ('land_geo_polygon', '!=', False)]
        return []
