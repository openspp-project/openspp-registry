/** @odoo-module */

import {ProductsWidget} from "@point_of_sale/app/screens/product_screen/product_list/product_list";

export class IdRedemptionProductsWidget extends ProductsWidget {
    setup() {
        super.setup();
    }
    getProductListToNotDisplay() {
        const products = super.getProductListToNotDisplay();
        if (this.props.partner) {
            const productsNotToDisplay = [];
            const list = this.pos.db.get_product_by_category(this.selectedCategoryId);
            for (let i = 0; i < list.length; i++) {
                if (
                    !list[i].entitlement_partner_id ||
                    list[i].entitlement_partner_id[0] !== this.props.partner.id
                ) {
                    productsNotToDisplay.push(list[i].id);
                }
            }
            products.push(...productsNotToDisplay);
        }
        return products;
    }
}

IdRedemptionProductsWidget.template = "spp_pos_id_redemption.IdRedemptionProductsWidget";
IdRedemptionProductsWidget.props = {
    partner: {type: Object, optional: true},
};
