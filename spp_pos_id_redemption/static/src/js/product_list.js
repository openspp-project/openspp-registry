/** @odoo-module */

import {ProductsWidget} from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import {onWillUpdateProps} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(ProductsWidget.prototype, {
    setup() {
        super.setup();
        this.state = Object.assign(this.state, {partner: this.props.partner});
        onWillUpdateProps((nextProps) => {
            this.state.partner = nextProps.partner;
        });
    },
    getProductListToNotDisplay() {
        const products = super.getProductListToNotDisplay();
        if (this.state.partner) {
            const productsNotToDisplay = [];
            const list = this.pos.db.get_product_by_category(this.selectedCategoryId);
            for (let i = 0; i < list.length; i++) {
                if (
                    !list[i].entitlement_partner_id ||
                    list[i].entitlement_partner_id[0] !== this.state.partner.id
                ) {
                    productsNotToDisplay.push(list[i].id);
                }
            }
            products.push(...productsNotToDisplay);
        }
        return products;
    },
});
