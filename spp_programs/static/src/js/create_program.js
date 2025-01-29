/** @odoo-module **/

import {ListController} from "@web/views/list/list_controller";
import {onWillStart} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(ListController.prototype, {
    setup() {
        super.setup();
        onWillStart(async () => {
            const is_g2p_admin = await this.userService.hasGroup("g2p_registry_base.group_g2p_admin");
            const is_program_manager = await this.userService.hasGroup("g2p_programs.g2p_program_manager");
            const is_create_program = await this.userService.hasGroup(
                "spp_programs.create_program_cycle_entitlement"
            );
            this.canCreateProgram = is_g2p_admin || is_program_manager || is_create_program;
        });
    },
});
