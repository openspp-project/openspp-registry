/** @odoo-module **/

import {ImportRecords} from "@base_import/import_records/import_records";

import {patch} from "@web/core/utils/patch";

patch(ImportRecords.prototype, {
    getAdditionalContext() {
        const {context, resModel} = this.env.searchModel;
        const additionalContext = {};
        if (resModel === "res.partner") {
            if (context.default_is_registrant) {
                additionalContext.default_is_registrant = context.default_is_registrant;
            }
            if (context.default_is_group) {
                additionalContext.default_is_group = context.default_is_group;
            }
            if (context.default_kind) {
                additionalContext.default_kind = context.default_kind;
            }
        }
        return additionalContext;
    },
    importRecords() {
        const {context, resModel} = this.env.searchModel;
        const additionalContext = this.getAdditionalContext();
        this.action.doAction({
            type: "ir.actions.client",
            tag: "import",
            params: {model: resModel, context, additionalContext},
        });
    },
});
