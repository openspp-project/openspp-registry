/** @odoo-module */

import {PosDB} from "@point_of_sale/app/store/db";
import {patch} from "@web/core/utils/patch";

patch(PosDB.prototype, {
    get_product_by_category(category_id) {
        this.limit = 999999;
        return super.get_product_by_category(category_id);
    },
});
