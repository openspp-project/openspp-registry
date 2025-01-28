import logging

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class CustomOpenIDVCIssuer(models.Model):
    _inherit = "g2p.openid.vci.issuers"

    @api.constrains("auth_allowed_issuers", "issuer_type")
    def onchange_auth_allowed_issuers(self):
        for rec in self:
            if not rec.auth_allowed_issuers:
                args = [rec, f"set_default_auth_allowed_issuers_{rec.issuer_type}"]
                if hasattr(*args):
                    getattr(*args)()

    def sign_and_issue_credential(self, credential: dict) -> dict:
        self.ensure_one()

        ld_proof = self.build_empty_ld_proof()

        signature = self.get_encryption_provider().jwt_sign(
            {"credential": credential, "proof": ld_proof},
            include_payload=False,
            include_certificate=True,
            include_cert_hash=True,
        )
        ld_proof["jws"] = signature
        ret = dict(credential)
        ret["proof"] = ld_proof
        return ret

    def get_auth_jwks(
        self,
        auth_issuer: str,
        auth_allowed_issuers: list[str],
        auth_allowed_jwks_urls: list[str],
    ):
        self.ensure_one()
        jwk_url = None
        try:
            jwk_url = auth_allowed_jwks_urls[auth_allowed_issuers.index(auth_issuer)]
        except Exception:
            jwk_url = f'{auth_issuer.rstrip("/")}/.well-known/jwks.json'
        _logger.info(f"Getting JWKS from {jwk_url}")
        return requests.get(jwk_url, timeout=20).json()
