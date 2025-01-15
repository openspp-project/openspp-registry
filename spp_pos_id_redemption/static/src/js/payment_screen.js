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
        super._finalizeValidation();

        // Get location data using async/await
        const {latitude, longitude} = await getLocation();

        // Process orderlines
        for (const orderline of this.pos.get_order().orderlines) {
            if (orderline.product.created_from_entitlement) {
                const productId = orderline.product.id;
                await this.orm.call("product.template", "redeem_voucher", [productId, latitude, longitude]);
                orderline.product.voucher_redeemed = true;
            }
        }
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
