from odoo import models


class CustomOpenIDVCIssuer(models.Model):
    _inherit = "g2p.openid.vci.issuers"

    def set_from_static_file_Registry(
        self, module_name="spp_openid_vci_individual", file_name="", field_name="", **kwargs
    ):
        return super().set_from_static_file_Registry(
            module_name=module_name, file_name=file_name, field_name=field_name, **kwargs
        )

    def set_default_auth_allowed_issuers_Registry(self):
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url").rstrip("/")
        endpoint = "/api/v1/security"
        self.auth_allowed_issuers = f"{web_base_url}{endpoint}"
