/** @odoo-module */

import {ProductsWidget} from "@point_of_sale/app/screens/product_screen/product_list/product_list";

export class IdRedemptionProductsWidget extends ProductsWidget {
    setup() {
        super.setup();
    }
}

IdRedemptionProductsWidget.template = "spp_pos_id_redemption.IdRedemptionProductsWidget";
IdRedemptionProductsWidget.props = {
    partner: {type: Object, optional: true},
};
