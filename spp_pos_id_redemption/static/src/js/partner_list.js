/** @odoo-module */

import {PartnerListScreen} from "@point_of_sale/app/screens/partner_list/partner_list";
import {patch} from "@web/core/utils/patch";

patch(PartnerListScreen.prototype, {
    clickPartner(partner) {
        super.clickPartner(partner);
        this.clearAllLines();
    },

    clearAllLines(){
        var order = this.pos.get_order();
        var lines = order.get_orderlines();
        if (lines.length){
            lines.filter(line => line.get_product())
                        .forEach(line => order.removeOrderline(line));
        }
    }
});
