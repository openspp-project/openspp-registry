/** @odoo-module */

import {PosStore} from "@point_of_sale/app/store/pos_store";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async selectPartner() {
        const currentOrder = this.get_order();
        if (!currentOrder) {
            return;
        }
        const currentPartner = currentOrder.get_partner();
        if (currentPartner && currentOrder.getHasRefundLines()) {
            this.popup.add(ErrorPopup, {
                title: _t("Can't change customer"),
                body: _t(
                    "This order already has refund lines for %s. We can't change the customer associated to it. Create a new order for the new customer.",
                    currentPartner.name
                ),
            });
            return;
        }
        const {confirmed, payload: newPartner} = await this.showTempScreen("PartnerListScreen", {
            partner: currentPartner,
        });
        if (confirmed) {
            currentOrder.set_partner(newPartner);
            const entitlements = await this._getEntitlementsProducts(newPartner);
            return entitlements;
        }
    },

    async _getEntitlementsProducts(currentPartner) {
        const foundEntitlementsIds = await this._searchEntitlementsProducts(currentPartner);
        if (foundEntitlementsIds.length === 1) {
            let product = this.db.get_product_by_id(foundEntitlementsIds[0].id);
            if (!product) {
                // If product is not loaded in POS, load it
                await this._addProducts([foundEntitlementsIds[0].id]);
                // Assume that the result is unique.
                product = this.db.get_product_by_id(foundEntitlementsIds[0].id);
            }
            return product;
        } else if (foundEntitlementsIds.length > 1) {
            return foundEntitlementsIds;
        }
        return false;
    },
    async _searchEntitlementsProducts(currentPartnerID) {
        const foundEntitlementsIds = await this.orm.silent.call("product.product", "search_read", [], {
            domain: [["entitlement_partner_id", "=", currentPartnerID.id]],
            fields: ["entitlement_id", "id"],
            order: "id desc",
        });
        return foundEntitlementsIds;
    },

    async addProductToCurrentOrder(product, options = {}) {
        const inside_entitlement = options.inside_entitlement || false;

        if (
            inside_entitlement !== product.created_from_entitlement ||
            (product.created_from_entitlement &&
                this.get_order().orderlines.some((orderline) => orderline.product.id === product.id))
        ) {
            return;
        }

        super.addProductToCurrentOrder(product, options);
    },
});
