/** @odoo-module **/

import {Component, onMounted, onWillStart, useRef} from "@odoo/owl";
import {loadBundle} from "@web/core/assets";

export class ChartComponent extends Component {
    setup() {
        onMounted(() => this.renderChart());
        this.canvasRef = useRef("canvas");

        this.chartTitle = "";
        const chartTypesWithTitle = ["pie", "doughnut"];
        if (chartTypesWithTitle.includes(this.props.chart_type)) {
            this.chartTitle = this.props.data_label;
        }

        onWillStart(async () => {
            return Promise.all([
                // Load external JavaScript and CSS libraries.
                loadBundle({
                    jsLibs: [
                        // "/awesome_dashboard/static/lib/chart-js.4.4.4/chart.umd.min.js",
                        "https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js",
                    ],
                }),
            ]);
        });
    }

    renderChart() {
        const ctx = this.canvasRef.el.getContext("2d");

        new Chart(ctx, {
            type: this.props.chart_type,
            data: {
                labels: this.props.labels,
                datasets: [
                    {
                        label: this.props.data_label,
                        data: this.props.data,
                        backgroundColor: this.props.backgroundColor,
                        hoverOffset: 2,
                    },
                ],
            },
            options: {...this.props.options},
        });
    }
}

ChartComponent.template = "spp_dashboard_base.ChartComponentTemplate";
ChartComponent.props = {
    chart_type: {type: String, optional: true},
    labels: {type: Array, optional: true},
    data_label: {type: String, optional: true},
    data: {type: Array, optional: true},
    backgroundColor: {type: Array, optional: true},
    options: {type: Object, optional: true},
    size: {type: String, optional: true},
};
ChartComponent.defaultProps = {
    chart_type: "pie",
    labels: ["Red", "Blue", "Yellow"],
    data_label: "Number of Colors",
    data: [300, 50, 150],
    backgroundColor: ["rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 205, 86)"],
    options: {
        maintainAspectRatio: true,
        aspectRatio: 2,
    },
    size: "col-md-6",
};
