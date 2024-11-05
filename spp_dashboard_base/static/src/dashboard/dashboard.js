/** @odoo-module **/
import {Component, onWillStart, useState} from "@odoo/owl";
import {CardBoardComponent} from "../card_board/card_board";
import {ChartComponent} from "../chart/chart";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SppDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({hierarchy: []});
        this.card_board_data = {};
        onWillStart(this.onWillStart);
        this.dashboard_title = "Dashboard";
    }

    async onWillStart() {
        // Super this function to get data from the server
        // sample
        // this.dashboard_data = await this.orm.call("res.partner", "get_data", []);
    }
}

SppDashboard.template = "spp_dashboard_base.dashboard_page";
SppDashboard.components = {ChartComponent, CardBoardComponent};

registry.category("actions").add("spp_dashboard_tag", SppDashboard);
