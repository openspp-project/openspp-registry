/** @odoo-module **/
import {ProductScreen} from "@point_of_sale/app/screens/product_screen/product_screen";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.sound = useService("sound");
        this.orm = useService("orm");
    },

    async updateSelectedOrderline({buffer, key}) {
        if (this.currentOrder.get_selected_orderline()) {
            const selectedProduct = this.currentOrder.get_selected_orderline().get_product();

            const result = await this.orm.call("product.template", "get_is_locked", [selectedProduct.id]);
            console.log("DEBUG: " + result.is_locked);

            if (result.is_locked && !(String(key) === "Backspace")) {
                this.sound.play("error");
            } else {
                return super.updateSelectedOrderline({buffer, key});
            }
        } else {
            return super.updateSelectedOrderline({buffer, key});
        }
    },
});
