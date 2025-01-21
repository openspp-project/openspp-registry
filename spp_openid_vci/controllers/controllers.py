import json
import logging

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
        enc = request.env.ref("g2p_encryption.encryption_provider_default")

        verified, jwt = enc.jwt_verify_jwcrypto(jws)

        if not verified:
            return False
        return jwt

    @route("/verify/vc", type="http", auth="none", methods=["Post"], csrf=False)
    def verify_vc(self):
        data = request.httprequest.data or "{}"
        data = json.loads(data)

        jws = data.get("jws")

        if not jws:
            return self.error_wrapper(400, "No JWS provided.")

        jwt = self.verify_jws(jws)
        if jwt is False:
            return self.error_wrapper(401, "Invalid JWS provided.")

        return self.response_wrapper(200, {"verified": True, "jwt": jwt.serialize()})
