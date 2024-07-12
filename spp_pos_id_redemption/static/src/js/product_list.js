/** @odoo-module */

import {ProductsWidget} from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import {onWillUpdateProps} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {CategorySelector} from "@point_of_sale/app/generic_components/category_selector/category_selector";
import {Input} from "@point_of_sale/app/generic_components/inputs/input/input";
import {IdRedemptionProductCard} from "@spp_pos_id_redemption/js/product_card";

patch(ProductsWidget.prototype, {
    setup() {
        super.setup();
        this.state = Object.assign(this.state, {partner: this.props.partner});
        onWillUpdateProps((nextProps) => {
            this.state.partner = nextProps.partner;
        });
        this.list = [];
        this.partner_product_mapper = {};
    },
    getProductListToNotDisplay() {
        const products = super.getProductListToNotDisplay();
        if (this.list.length === 0) {
            // To prevent multiple calls to get_product_by_category
            this.list = this.pos.db.get_product_by_category(this.selectedCategoryId);
        }

        if (this.state.partner && !(this.state.partner.id in this.partner_product_mapper)) {
            // Created a mapper to store the products that are not to be displayed
            // for a particular partner
            // this is to prevent multiple filtering of a product list
            this.partner_product_mapper[this.state.partner.id] = this.list
                .filter(
                    (product) =>
                        (this.state.partner &&
                            (!product.entitlement_partner_id ||
                                product.entitlement_partner_id[0] !== this.state.partner.id)) ||
                        (product.created_from_entitlement && product.voucher_redeemed) ||
                        (!this.state.partner && product.entitlement_partner_id)
                )
                .map((product) => product.id);
        }

        if (this.state.partner) {
            return [...products, ...this.partner_product_mapper[this.state.partner.id]];
        }
        const productNotToDisplay = this.list
            .filter((product) => !this.state.partner && product.entitlement_partner_id)
            .map((product) => product.id);
        return [...products, ...productNotToDisplay];
    },
});
ProductsWidget.template = "spp_pos_id_redemption.IdRedemptionProductWidget";
ProductsWidget.components = {IdRedemptionProductCard, CategorySelector, Input};
