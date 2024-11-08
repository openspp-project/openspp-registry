/** @odoo-module **/

import {ListRenderer} from "@web/views/list/list_renderer";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
    },

    async onCellClicked(record, column, ev) {
        console.log(record);
        if (record.resModel === "g2p.program") {
            var result = await this.orm.call("g2p.program", "open_program_form", [record.resId]);
            this.actionService.doAction(
                {
                    name: result.name,
                    type: "ir.actions.act_window",
                    res_model: result.res_model,
                    views: [[result.view_id, "form"]],
                    res_id: result.res_id,
                    target: result.target,
                    context: result.context,
                },
                {clear_breadcrumbs: true}
            );
        } else {
            super.onCellClicked(record, column, ev);
        }
    },
});
