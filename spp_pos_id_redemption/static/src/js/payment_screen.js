/** @odoo-module */

import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {patch} from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async _finalizeValidation() {
        super._finalizeValidation();
        for (const orderline of this.pos.get_order().orderlines) {
            if (orderline.product.created_from_entitlement) {
                const productId = orderline.product.id;
                await this.orm.call("product.template", "redeem_voucher", [productId]);
                orderline.product.voucher_redeemed = true;
            }
        }
    },
});
