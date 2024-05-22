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
        const list = this.pos.db.get_product_by_category(this.selectedCategoryId);

        const productsNotToDisplay = list
            .filter(
                (product) =>
                    (this.state.partner &&
                        (!product.entitlement_partner_id ||
                            product.entitlement_partner_id[0] !== this.state.partner.id)) ||
                    (product.created_from_entitlement && product.voucher_redeemed) ||
                    (!this.state.partner && product.entitlement_partner_id)
            )
            .map((product) => product.id);

        return [...products, ...productsNotToDisplay];
    },
});
