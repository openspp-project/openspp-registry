import logging

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
        # Override the method to get the JWKS from the encryption providers
        self.ensure_one()
        encryption_providers = self.env["g2p.encryption.provider"].sudo().search([])
        jwks = []
        for prov in encryption_providers:
            try:
                prov_jwks = prov.get_jwks()
                jwks.extend(prov_jwks.get("keys", []) if prov_jwks else [])
            except Exception:
                _logger.exception("Unable to get JWKS from list of encryption providers")
        return {"keys": jwks}
