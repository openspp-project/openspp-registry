import json
import logging

import requests
import werkzeug.wrappers

from odoo.http import Controller, request, route
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class SppOpenIDVCIController(Controller):
    def response_wrapper(self, status, data):
        return werkzeug.wrappers.Response(
            status=status,
            content_type="application/json; charset=utf-8",
            response=json.dumps(data, default=date_utils.json_default) if data else None,
        )

    def error_wrapper(self, code, message):
        error = {"error": {"code": code, "message": message}}
        return self.response_wrapper(code, error)

    def verify_jws(self, jws):
        enc = request.env.ref("g2p_encryption.encryption_provider_default").sudo()

        try:
            verified, jwt = enc.jwt_verify_jwcrypto(jws)
        except Exception as e:
            _logger.error(e)
            return False

        if not verified:
            return False
        return jwt

    def get_individual_fields(self):
        return ["name"]

    @route("/api/v1/registry/individual/<int:individual_id>", type="http", auth="none", methods=["GET"], csrf=False)
    def get_individual_data(self, individual_id):
        data = request.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return self.response_wrapper(
                400,
                {
                    "error": "Bad Request",
                    "error_description": "data must be in JSON format.",
                },
            )
        api_key = data.get("api_key")
        if not api_key:
            return self.error_wrapper(401, "Missing authentication credentials.")
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
        if not user_id:
            return self.error_wrapper(401, "Invalid authentication credentials.")

        individual = request.env["res.partner"].sudo().search([("id", "=", individual_id)], limit=1)
        if not individual:
            return self.error_wrapper(404, "Individual not found.")
        return self.response_wrapper(200, {"individual": individual.read(self.get_individual_fields())[0]})

    @route("/verify/vc", type="http", auth="none", methods=["POST"], csrf=False)
    def verify_vc(self):
        data = request.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return self.response_wrapper(
                400,
                {
                    "error": "Bad Request",
                    "error_description": "data must be in JSON format.",
                },
            )

        # Check for authentication credentials
        api_key = data.get("api_key")

        if not api_key:
            return self.error_wrapper(401, "Missing authentication credentials.")

        # Verify credentials against res.users
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)

        if not user_id:
            return self.error_wrapper(401, "Invalid authentication credentials.")

        jws = data.get("jws")
        if not jws:
            return self.error_wrapper(400, "No JWS provided.")

        jwt = self.verify_jws(jws)
        if jwt is False:
            return self.error_wrapper(401, "Invalid JWS provided.")

        data = json.loads(jwt.claims)
        individual_id_url = data.get("credential", {}).get("credentialSubject", {}).get("id")

        response = requests.get(individual_id_url, json={"api_key": api_key})
        if response.status_code != 200:
            response_data = response.json()
            error_code = response_data.get("error", {}).get("code", "Unknown error")
            error_message = response_data.get("error", {}).get("message", "Unknown error")
            return self.error_wrapper(error_code, error_message)

        return self.response_wrapper(200, {"verified": True, **response.json()})
