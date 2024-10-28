/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useFileViewer} from "@web/core/file_viewer/file_viewer_hook";
import {useService} from "@web/core/utils/hooks";

export class PreviewRecordWidget extends Component {
    setup() {
        this.store = useService("mail.store");
        this.orm = useService("orm");
        this.fileViewer = useFileViewer();
    }

    async onFilePreview(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        const resId = this.props.record.resId;
        const resModel = this.props.record.resModel;

        const [record] = await this.orm.read(resModel, [resId], ["content", "name", "mimetype"]);

        if (!record || !record.content) {
            console.error("No file found!");
            return;
        }

        const binaryData = atob(record.content);
        const arrayBuffer = new Uint8Array(binaryData.length);

        for (let i = 0; i < binaryData.length; i++) {
            arrayBuffer[i] = binaryData.charCodeAt(i);
        }

        const blob = new Blob([arrayBuffer], {type: record.mimetype});
        const fileUrl = URL.createObjectURL(blob);

        if (record.mimetype === "application/pdf") {
            window.open(fileUrl, "_blank");
        } else {
            const attachment = this.store.Attachment.insert({
                id: resId,
                filename: record.name || "",
                name: record.name || "",
                mimetype: record.mimetype,
                model_name: resModel,
                url: fileUrl,
            });

            this.fileViewer.open(attachment);
        }
    }
}

PreviewRecordWidget.template = "dms.PreviewBinaryField";

const previewRecordWidget = {
    component: PreviewRecordWidget,
    display_name: "Preview File Widget",
    supportedTypes: ["binary"],
};

registry.category("fields").add("preview_widget", previewRecordWidget);
