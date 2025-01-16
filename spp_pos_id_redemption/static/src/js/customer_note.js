/** @odoo-module */

import {_t} from "@web/core/l10n/translation";
import {OrderlineCustomerNoteButton} from "@point_of_sale/app/screens/product_screen/control_buttons/customer_note_button/customer_note_button";
import {TextAreaPopup} from "@point_of_sale/app/utils/input_popups/textarea_popup";
import {patch} from "@web/core/utils/patch";

patch(OrderlineCustomerNoteButton.prototype, {
    async onClick() {
        const selectedOrderline = this.pos.get_order().get_selected_orderline();
        // FIXME POSREF can this happen? Shouldn't the orderline just be a prop?
        if (!selectedOrderline) {
            return;
        }
        const {confirmed, payload: inputNote} = await this.popup.add(TextAreaPopup, {
            startingValue: selectedOrderline.get_customer_note(),
            title: _t("Add Beneficiary Note"),
        });

        if (confirmed) {
            selectedOrderline.set_customer_note(inputNote);
        }
    },
});
