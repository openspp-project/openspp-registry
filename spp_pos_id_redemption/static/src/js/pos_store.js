/** @odoo-module */

import {PosStore} from "@point_of_sale/app/store/pos_store";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
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
