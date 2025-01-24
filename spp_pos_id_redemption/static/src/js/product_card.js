/** @odoo-module */

import {ProductCard} from "@point_of_sale/app/generic_components/product_card/product_card";

export class IdRedemptionProductCard extends ProductCard {
    setup() {
        super.setup();
    }
}

IdRedemptionProductCard.template = "spp_pos_id_redemption.IdRedemptionProductCard";
IdRedemptionProductCard.props = {
    program_id_str: {type: String, optional: true},
    cycle_id_str: {type: String, optional: true},
    entitlement_valid_until: {type: Date, optional: true},
};
