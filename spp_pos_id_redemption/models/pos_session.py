from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        params = super()._loader_params_product_product()
        params["search_params"]["fields"].extend(
            [
                "is_locked",
                "entitlement_id",
                "entitlement_partner_id",
                "created_from_entitlement",
                "voucher_redeemed",
            ]
        )
        return params
