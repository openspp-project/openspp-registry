/** @odoo-module */

import {PaymentScreen} from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {patch} from "@web/core/utils/patch";

// Utility function to wrap getCurrentPosition in a Promise
function getLocation() {
    return new Promise((resolve) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                    });
                },
                (error) => {
                    console.error(`Geolocation error: ${error.message}`);
                    resolve({latitude: null, longitude: null}); // Proceed without location
                }
            );
        } else {
            console.error("Geolocation is not supported by this browser.");
            resolve({latitude: null, longitude: null}); // Proceed without location
        }
    });
}

patch(PaymentScreen.prototype, {
    async _finalizeValidation() {
        const {latitude, longitude} = await getLocation();

        const promises = this.pos.get_order().orderlines.map(async (orderline) => {
            if (orderline.product.created_from_entitlement) {
                const productId = orderline.product.id;

                if (orderline.quantity >= 1) {
                    await this.orm.call("product.template", "redeem_voucher", [
                        productId,
                        latitude,
                        longitude,
                    ]);
                    orderline.product.voucher_redeemed = true;
                } else {
                    await this.orm.call("product.template", "undo_redeem_voucher", [
                        productId,
                        latitude,
                        longitude,
                    ]);
                    orderline.product.voucher_redeemed = false;
                }
            }
        });

        await Promise.all(promises); // Wait for all promises to resolve

        super._finalizeValidation();
    },

    backToPOS() {
        const paymentLines = this.currentOrder.get_paymentlines();
        this._removeCurrentPaymentLines(paymentLines);
        this.pos.showScreen("ProductScreen");
    },

    async _removeCurrentPaymentLines(paymentLines) {
        for await (const line of paymentLines) {
            this.currentOrder.remove_paymentline(line);
        }
    },
});
