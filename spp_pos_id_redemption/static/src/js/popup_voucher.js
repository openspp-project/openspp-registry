/** @odoo-module */

import {EntitlementPopup} from "@spp_pos/js/popup_voucher";
import {IdRedemptionProductsWidget} from "@spp_pos_id_redemption/js/entitlement_product_list";
import {patch} from "@web/core/utils/patch";

patch(EntitlementPopup.prototype, {
    setup() {
        super.setup();
        let order = this.pos.get_order();
        if (!order) {
            order = this.pos.add_new_order();
        }
        if (order.partner) {
            this.partner = order.partner;
        }
    },
});

EntitlementPopup.template = "spp_pos_id_redemption.EntitlementPopup";
EntitlementPopup.components = {IdRedemptionProductsWidget};
