/** @odoo-module **/

import {Component} from "@odoo/owl";

export class CardBoardComponent extends Component {}

CardBoardComponent.template = "spp_dashboard_base.CardBoardTemplate";
CardBoardComponent.props = {
    title: {type: String, optional: true},
    data: {type: [String, Number], optional: true},
    size: {type: String, optional: true},
};
CardBoardComponent.defaultProps = {
    title: "Title",
    data: "Data",
    size: "col-md-4",
};
