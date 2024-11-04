import base64
import json

import werkzeug.wrappers

from odoo.http import Controller, request, route
from odoo.tools import date_utils

from odoo.addons.spp_oauth.tools import OpenSPPOAuthJWTException, verify_and_decode_signature

ALLOWED_LAYER_TYPE = [
    "point",
    "line",
    "polygon",
]

ALLOWED_SPATIAL_RELATION = [
    "intersects",
    "within",
    "contains",
]


def response_wrapper(status, data):
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=date_utils.json_default) if data else None,
    )


def error_wrapper(code, message):
    error = {"error": {"code": code, "message": message}}
    return response_wrapper(code, error)


def get_auth_header(headers, raise_exception=False):
    """
    The function `get_auth_header` retrieves the Authorization header from a given dictionary of headers
    and optionally raises an exception if the header is missing or does not start with "Bearer " or
    "Basic ".

    :param headers: The `get_auth_header` function takes two parameters:
    :param raise_exception: The `raise_exception` parameter in the `get_auth_header` function is a
    boolean flag that determines whether an exception should be raised if the authentication header is
    missing or does not start with "Bearer " or "Basic ". If `raise_exception` is set to `True`, an
    error response with status, defaults to False (optional)
    :return: The function `get_auth_header` is returning the value of the `auth_header` variable, which
    is either the value of the "Authorization" or "authorization" key from the `headers` dictionary. If
    the `auth_header` does not start with "Bearer " or "Basic ", and `raise_exception` is `False`, then
    it will return `None`. If `raise_exception` is
    """
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not (auth_header.startswith("Bearer ") or auth_header.startswith("Basic ")):
        if raise_exception:
            error = {
                "error": "Unauthorized",
                "error_description": "Your token could not be authenticated.",
            }
            return response_wrapper(401, error)
    return auth_header


def verify_and_decode_token(access_token):
    """
    The function `verify_and_decode_token` decodes a base64 encoded access token and checks if it
    matches a client token in a database.

    :param access_token: It looks like the code you provided is a function that verifies and decodes a
    given access token. However, the code is missing the import statement for the `base64` module, and
    it seems to be using some custom environment variables like `request` and `sudo()` which are not
    defined in
    :return: The function `verify_and_decode_token` returns a boolean value. It returns `True` if a
    client with the decoded token exists in the database, and `False` if an exception occurs during the
    decoding process or if the client does not exist.
    """
    try:
        # Decode the base64 encoded string
        decoded_bytes = base64.b64decode(access_token)
        # Convert the bytes to a string
        decoded_string = decoded_bytes.decode("utf-8")

        client = (
            request.env["spp.gis.api.client.credential"]
            .sudo()
            .search(
                [("client_token", "=", decoded_string)],
                limit=1,
            )
        )

        return bool(client)
    except Exception:
        return False


def verify_auth_header():
    """
    The function `verify_auth_header` extracts and verifies an access token from the authorization
    header of an HTTP request.
    :return: The function `verify_auth_header()` returns the result of the verification process based on
    the type of authentication header provided. If the header starts with "Bearer ", it decodes the
    access token and verifies the signature. If the header starts with "Basic ", it decodes the access
    token and verifies it. The function returns the verification result.
    """
    auth_header = get_auth_header(request.httprequest.headers, raise_exception=True)

    if auth_header.startswith("Bearer "):
        access_token = auth_header.replace("Bearer ", "").replace("\\n", "").encode("utf-8")
        try:
            verify_and_decode_signature(access_token)
            verified = True
        except OpenSPPOAuthJWTException:
            verified = False

    elif auth_header.startswith("Basic "):
        access_token = auth_header.replace("Basic ", "").replace("\\n", "").encode("utf-8")
        verified = verify_and_decode_token(access_token)

    return verified


def validate_locational_query_data(data):
    """
    The function `validate_locational_query_data` checks the validity of locational query data including
    layer type, latitude, longitude, and spatial relation.

    :param data: The function `validate_locational_query_data(data)` is designed to validate locational
    query data based on certain criteria. Here's an explanation of the parameters used in the function:
    :return: The function `validate_locational_query_data` is returning an error message wrapped in a
    response with a status code of 400 (Bad Request) if any of the validation conditions are not met. If
    all the validation checks pass, it returns `None`, indicating that the data passed the validation
    successfully.
    """
    if not data:
        return error_wrapper(400, "Bad Request. Request data is empty.")
    elif not data.get("LayerType"):
        return error_wrapper(400, "Bad Request. LayerType is required.")
    elif data["LayerType"] not in ALLOWED_LAYER_TYPE:
        return error_wrapper(400, "Bad Request. Invalid LayerType.")
    elif not data.get("Latitude") or not data.get("Longitude"):
        return error_wrapper(400, "Bad Request. Latitude and Longitude are required.")
    elif data["Latitude"] < -90 or data["Latitude"] > 90:
        return error_wrapper(400, "Bad Request. Latitude must be between -90 and 90.")
    elif data["Longitude"] < -180 or data["Longitude"] > 180:
        return error_wrapper(400, "Bad Request. Longitude must be between -180 and 180.")
    elif not data.get("SpatialRelation"):
        return error_wrapper(400, "Bad Request. SpatialRelation is required.")
    elif data["SpatialRelation"] not in ALLOWED_SPATIAL_RELATION:
        return error_wrapper(400, "Bad Request. Invalid SpatialRelation.")
    return None


def validate_attribute_query_data(data):
    """
    The function `validate_attribute_query_data` checks if the required attributes are present in the
    input data and returns an error message if any are missing.

    :param data: The `validate_attribute_query_data` function takes a dictionary `data` as input and
    checks if it meets certain criteria. It checks if the `data` dictionary is not empty, if it contains
    the keys "AttributeName", "Operator", and "Value". If any of these conditions are not met,
    :return: The function `validate_attribute_query_data` returns an error message with a status code of
    400 if any of the required attributes ("AttributeName", "Operator", "Value") are missing in the
    input data. If the input data is empty, it also returns an error message with a status code of 400.
    If all required attributes are present in the input data, it returns `None`.
    """
    if not data:
        return error_wrapper(400, "Bad Request. Request data is empty.")
    elif not data.get("AttributeName"):
        return error_wrapper(400, "Bad Request. AttributeName is required.")
    elif not data.get("Operator"):
        return error_wrapper(400, "Bad Request. Operator is required.")
    elif not data.get("Value"):
        return error_wrapper(400, "Bad Request. Value is required.")
    return None


class SppGisApiController(Controller):
    @route(
        "/v1/gisBB/oauth2/client/token",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def auth_get_access_token(self, **kwargs):
        req = request
        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return response_wrapper(
                400,
                {
                    "error": "Bad Request",
                    "error_description": "data must be in JSON format.",
                },
            )

        client_id = data.get("client_id", "")
        client_secret = data.get("client_secret", "")

        if not all([client_id, client_secret]):
            error = {
                "error": "Bad Request",
                "error_description": "client_id and client_secret are required.",
            }
            return response_wrapper(400, error)

        client = (
            req.env["spp.gis.api.client.credential"]
            .sudo()
            .search(
                [("client_id", "=", client_id), ("client_secret", "=", client_secret)],
                limit=1,
            )
        )

        if not client:
            error = {
                "error": "Unauthorized",
                "error_description": "Invalid client id or secret.",
            }
            return response_wrapper(401, error)

        access_token = client.generate_access_token()

        data = {
            "access_token": access_token,
            "token_type": "Bearer",
        }
        return response_wrapper(200, data)

    @route(
        "/v1/gisBB/query/locationalQuery",
        auth="none",
        methods=["POST"],
        type="http",
        csrf=False,
    )
    def locational_query(self, **kwargs):
        if not verify_auth_header():
            return error_wrapper(401, "Invalid Access Token.")

        lower_case = ["LayerType", "SpatialRelation"]
        request_data = json.loads(request.httprequest.data.decode("utf-8"))
        request_data = {key: value.lower() if key in lower_case else value for key, value in request_data.items()}

        if locational_data_error := validate_locational_query_data(request_data):
            return locational_data_error

        model_name = request_data.get("model_name", "res.partner")
        model = request.env[model_name].sudo()

        feature_collection = model.gis_locational_query(
            longitude=request_data["Longitude"],
            latitude=request_data["Latitude"],
            layer_type=request_data["LayerType"],
            spatial_relation=request_data.get("SpatialRelation", "intersects"),
            distance=request_data.get("Distance", None),
        )

        return response_wrapper(200, feature_collection)

    @route(
        "/v1/gisBB/query/attributeQuery",
        auth="none",
        methods=["POST"],
        type="http",
        csrf=False,
    )
    def attribute_query(self, **kwargs):
        if not verify_auth_header():
            return error_wrapper(401, "Invalid Access Token.")
        lower_case = ["AttributeName", "Operator"]
        request_data = json.loads(request.httprequest.data.decode("utf-8"))
        request_data = {key: value.lower() if key in lower_case else value for key, value in request_data.items()}

        if attribute_data_error := validate_attribute_query_data(request_data):
            return attribute_data_error

        model_name = request_data.get("model_name", "res.partner")
        model = request.env[model_name].sudo()

        records = model.search([(request_data["AttributeName"], request_data["Operator"], request_data["Value"])])

        layer_types = ["point", "line", "polygon"]

        field_type = [model.get_field_type_from_layer_type(layer_type) for layer_type in layer_types]

        fields = model.get_fields_of_type(field_type)

        features = []
        for field in fields:
            features.extend(records.get_feature(field.name))
        feature_collection = model.convert_feature_to_featurecollection(features)

        return response_wrapper(200, feature_collection)

    # TODO: Implement this query in the future
    # @route(
    #     "/v1/gisBB/query/gisQuery",
    #     auth="none",
    #     methods=["POST"],
    #     type="http",
    #     csrf=False,
    # )
    # def gis_query(self, **kwargs):
    #     if not verify_auth_header():
    #         return error_wrapper(401, "Invalid Access Token.")

    #     data = {
    #         "header": "Valid Access Token.",
    #         "message": "correct access token.",
    #     }
    #     return response_wrapper(200, data)

    # TODO: Implement this query in the future
    # @route(
    #     "/v1/gisBB/query/discoveryQuery",
    #     auth="none",
    #     methods=["POST"],
    #     type="http",
    #     csrf=False,
    # )
    # def discovery_query(self, **kwargs):
    #     if not verify_auth_header():
    #         return error_wrapper(401, "Invalid Access Token.")

    #     data = {
    #         "header": "Valid Access Token.",
    #         "message": "correct access token.",
    #     }
    #     return response_wrapper(200, data)
