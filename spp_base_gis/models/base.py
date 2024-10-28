import logging

from shapely.geometry import mapping

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError

from .. import fields as geo_fields
from ..operators import Operator

_logger = logging.getLogger(__name__)

ALLOWED_LAYER_TYPE = list(Operator.ALLOWED_LAYER_TYPE.values())

# Interchange keys and values
RELATION_TO_OPERATION = {value: key for key, value in Operator.OPERATION_TO_RELATION.items()}


def is_valid_coordinates(latitude, longitude):
    """
    Checks if the provided latitude and longitude values are valid.

    This function checks if the latitude and longitude are of type int or float,
    and if they fall within the valid range for geographical coordinates.
    The valid range for latitude is -90 to 90 (inclusive), and for longitude is -180 to 180 (inclusive).

    Parameters:
    latitude (int, float): The latitude value to check. Should be a number between -90 and 90.
    longitude (int, float): The longitude value to check. Should be a number between -180 and 180.

    Returns:
    bool: True if the latitude and longitude are valid, False otherwise.
    """

    if not isinstance(latitude, int | float) or not isinstance(longitude, int | float):
        return False

    # Check latitude
    if latitude < -90 or latitude > 90:
        return False

    # Check longitude
    if longitude < -180 or longitude > 180:
        return False

    # If both checks pass, the coordinates are valid
    return True


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Add geo_type definition for geo fields"""
        res = super().fields_get(allfields=allfields, attributes=attributes)
        for f_name in res:
            field = self._fields.get(f_name)
            if field and field.type.startswith("geo_"):
                geo_type = {
                    "type": field.type,
                    "dim": int(field.dim),
                    "srid": field.srid,
                    "geo_type": field.geo_type,
                }
                res[f_name]["geo_type"] = geo_type
        return res

    @api.model
    def _get_gis_view(self):
        gis_view = (
            self.env["ir.ui.view"]
            .sudo()
            .search(
                [("model", "=", self._name), ("type", "=", "gis")],
                limit=1,
            )
        )
        if not gis_view:
            raise UserError(
                _("No GIS view defined for the model %s. Please create a view or modify view mode") % self._name,
            )
        return gis_view

    @api.model
    def set_gis_field_name(self, in_tuple):
        if not in_tuple:
            return in_tuple
        field_obj = self.env["ir.model.fields"]
        name = field_obj.browse(in_tuple[0]).name
        return (
            in_tuple[0],
            name,
            in_tuple[1],
            field_obj.browse(in_tuple[0]).field_description,
            field_obj.browse(in_tuple[0]).ttype,
        )

    @api.model
    def get_gis_layers(self, view_id=None, view_type="gis", **options):
        view_obj = self.env["ir.ui.view"]

        if not view_id:
            view = self._get_gis_view()
        else:
            view = view_obj.browse(view_id)
        gis_layers = {
            "backgrounds": view.raster_layer_ids.read(),
            "default_zoom": view.default_zoom,
        }

        layer_dict_list = view.data_layer_ids.read()
        res_model = view.data_layer_ids._name

        for layer_dict in layer_dict_list:
            layer_dict["attribute_field_id"] = self.set_gis_field_name(layer_dict.get("attribute_field_id", False))
            layer_dict["geo_field_id"] = self.set_gis_field_name(layer_dict.get("geo_field_id", False))
            layer_dict["resModel"] = res_model
            layer_dict["model"] = layer_dict["model_name"]

        gis_layers["actives"] = layer_dict_list
        return gis_layers

    @api.model
    def get_edit_info_for_gis_column(self, column):
        raster_obj = self.env["spp.gis.raster.layer"]

        field = self._fields.get(column)
        if not field or not isinstance(field, geo_fields.GeoField):
            raise ValueError(_("%s column does not exists or is not a geo field") % column)
        view = self._get_gis_view()
        raster = raster_obj.search([("view_id", "=", view.id)], limit=1)
        if not raster:
            raise MissingError(_("No raster layer for view %s") % (view.name,))
        return {
            "edit_raster": raster.read()[0],
            "srid": field.srid,
            "default_zoom": view.default_zoom,
            "default_center": view.default_center,
        }

    @api.model
    def get_edit_info_for_gis(self):
        view = self._get_gis_view()
        return {
            "default_zoom": view.default_zoom,
            "default_center": view.default_center,
        }

    @api.model
    def get_fields_of_type(self, field_type: str | list) -> list:
        """
        This Python function retrieves fields of a specified type from a model object.

        :param field_type: The `field_type` parameter in the `get_fields_of_type` method can be either a
        string or a list of strings. The method filters fields based on their type, which is specified
        by the `field_type` parameter. If `field_type` is a string, the method will return a
        :type field_type: str | list
        :return: The `get_fields_of_type` method returns a list of fields from the model that match the
        specified field type or types.
        """

        # Get the model
        model = self.env[self._name].sudo()

        # Filter fields by type
        if isinstance(field_type, str):
            fields = [field for field in model._fields.values() if field.type == field_type]
        elif isinstance(field_type, list):
            fields = [field for field in model._fields.values() if field.type in field_type]
        else:
            raise ValueError(_("Invalid field type: %s") % field_type)

        return fields

    @api.model
    def shape_to_geojson(self, shape):
        """
        The function `shape_to_geojson` converts a shape object to a GeoJSON format using the `mapping`
        function.

        :param shape: The `shape` parameter in the `shape_to_geojson` function is typically a geometric
        shape object, such as a Point, LineString, Polygon, etc., from a library like Shapely in Python.
        The `mapping` function is used to convert these geometric shapes into GeoJSON format,
        :return: The function `shape_to_geojson` is returning the GeoJSON representation of the input
        `shape` object by using the `mapping` function.
        """
        return mapping(shape)

    @api.model
    def convert_feature_to_featurecollection(self, features: list | dict) -> dict:
        """
        The function `convert_feature_to_featurecollection` converts a list of features into a GeoJSON
        FeatureCollection.

        :param features: The `features` parameter in the `convert_feature_to_featurecollection` function
        is expected to be a list of feature objects. These feature objects typically represent
        geographic features and are structured in a specific format, such as GeoJSON format. The
        function takes this list of features and wraps them in a GeoJSON
        :type features: list
        :return: A dictionary is being returned with the keys "type" and "features". The value of the
        "type" key is set to "FeatureCollection", and the value of the "features" key is set to the
        input parameter `features`, which is a list of features.
        """
        return {"type": "FeatureCollection", "features": features if isinstance(features, list) else [features]}

    @api.model
    def get_field_type_from_layer_type(self, layer_type):
        """
        The function `get_field_type_from_layer_type` maps a layer type to a corresponding field type
        for geographic data, raising a UserError if the layer type is invalid.

        :param layer_type: The `get_field_type_from_layer_type` function takes a `layer_type` as input
        and returns the corresponding field type based on a mapping defined in the `layer_type_mapping`
        dictionary. The mapping assigns a field type to each layer type - "point", "line", and "polygon"
        :return: The function `get_field_type_from_layer_type` returns the corresponding field type
        based on the given `layer_type`. If the `layer_type` is "point", it returns "geo_point". If the
        `layer_type` is "line", it returns "geo_line". If the `layer_type` is "polygon", it returns
        "geo_polygon". If the `layer_type` is not one
        """
        layer_type_mapping = {
            "point": "geo_point",
            "line": "geo_line",
            "polygon": "geo_polygon",
        }

        try:
            return layer_type_mapping[layer_type]
        except KeyError as e:
            raise UserError(_("Invalid layer type %s") % layer_type) from e

    @api.model
    def gis_locational_query(
        self, longitude: float, latitude: float, layer_type="polygon", spatial_relation="intersects", distance=None
    ):
        """
        The function `gis_locational_query` performs a spatial query based on given coordinates, layer
        type, spatial relation, and optional distance.

        :param longitude: The `longitude` parameter is a float value representing the longitudinal
        coordinate of a location
        :type longitude: float
        :param latitude: Latitude is the angular distance of a location north or south of the earth's
        equator, measured in degrees. It ranges from -90 degrees (South Pole) to +90 degrees (North
        Pole)
        :type latitude: float
        :param layer_type: The `layer_type` parameter in the `gis_locational_query` function specifies
        the type of layer to query. It can be set to "polygon" or any other allowed layer type. If the
        provided `layer_type` is not in the list of allowed layer types, an error will be raised,
        defaults to polygon (optional)
        :param spatial_relation: The `spatial_relation` parameter in the `gis_locational_query` function
        determines the spatial relationship used in the query to filter the results. It specifies how
        the provided point (defined by the longitude and latitude) should relate to the geometries in
        the spatial layer being queried. The possible values for, defaults to intersects (optional)
        :param distance: The `distance` parameter in the `gis_locational_query` function is used to
        specify a distance in meters for a spatial query. If provided, the function will search for
        features within the specified distance from the given latitude and longitude coordinates. If the
        `distance` parameter is not provided (i.e
        :return: The function `gis_locational_query` returns a FeatureCollection containing features
        that match the specified criteria based on the provided longitude, latitude, layer type, spatial
        relation, and optional distance.
        """
        if not is_valid_coordinates(latitude, longitude):
            raise UserError(
                _("Invalid coordinates: latitude=%(latitude)s, longitude=%(longitude)s")
                % {"latitude": latitude, "longitude": longitude}
            )
        if layer_type not in ALLOWED_LAYER_TYPE:
            raise UserError(_("Invalid layer type %s") % layer_type)
        if spatial_relation not in Operator.POSTGIS_SPATIAL_RELATION.keys():
            raise UserError(_("Invalid spatial relation %s") % spatial_relation)
        if distance:
            if not isinstance(distance, int | float):
                raise UserError(_("Distance must be a number"))
            if distance <= 0:
                raise UserError(_("Distance must be a positive number"))

        layer_type = self.get_field_type_from_layer_type(layer_type)

        fields = self.get_fields_of_type(layer_type)

        features = []

        for field in fields:
            value_wkt = f"POINT({longitude} {latitude})"
            if distance:
                value = (value_wkt, distance)
            else:
                value = value_wkt

            domain = [(field.name, RELATION_TO_OPERATION[spatial_relation], value)]
            result = self.search(domain)
            if result:
                features.extend(result.get_feature(field.name))

        return self.convert_feature_to_featurecollection(features)

    def get_feature(self, field_name):
        """
        The function `get_feature` generates a list of features with specified properties for each
        record in a dataset.

        :param field_name: The `field_name` parameter in the `get_feature` method is used to specify the
        name of the field in the record object from which the geometry data will be extracted. This
        field name is dynamically retrieved using `getattr(rec, field_name)` within the method to get
        the geometry data for each record
        :return: The `get_feature` method returns a list of features, where each feature is a dictionary
        containing information about a record in the dataset. Each feature has a "type" key with the
        value "Feature", a "geometry" key with the geojson representation of the record's shape based on
        the specified field name, and a "properties" key with additional information such as the
        record's name.
        """
        features = []
        for rec in self:
            if hasattr(rec, field_name) and (geo_shape := getattr(rec, field_name)):
                feature = {
                    "type": "Feature",
                    "geometry": rec.shape_to_geojson(geo_shape),
                    "properties": {
                        "name": rec.name,
                        # TODO: Add more properties
                    },
                }
                features.append(feature)
        return features
