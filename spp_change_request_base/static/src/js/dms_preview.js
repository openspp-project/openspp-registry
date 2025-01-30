odoo.define("spp_change_request.dms_preview", function (require) {
    var field_registry = require("web.field_registry");
    var AbstractField = require("web.AbstractField");
    var preview = require("mail_preview_base.preview");
    var FieldPreviewViewer = preview.FieldPreviewViewer;

    var DocumentReader = AbstractField.extend({
        template: "dms_preview",
        events: {
            click: "_onClick",
        },
        init: function () {
            this._super.apply(this, arguments);

            const default_button_text = "View Attachment";
            const default_icon = "fa fa-fw o_button_icon fa-search";
            const default_classes = "btn btn-primary";
            var icon = "";
            if (this.attrs.icon) {
                icon = "fa fa-fw o_button_icon " + this.attrs.icon;
            }
            this.text = this.attrs.text || this.attrs.title || default_button_text;
            this.icon = icon || default_icon;
            this.classes = this.attrs.classes || this.attrs.classNames || default_classes;
        },
        _onClick: function () {
            var record = this.recordData;
            var fieldName = "content";
            var mimetype = record.mimetype;
            var type = mimetype.split("/").shift();
            if (type === "video" || type === "image" || mimetype === "application/pdf") {
                var attachmentViewer = new FieldPreviewViewer(
                    this,
                    [
                        {
                            mimetype: record.mimetype,
                            id: record.id,
                            fileType: this.mimetype_value,
                            name: record.name,
                        },
                    ],
                    record.id,
                    this.model,
                    fieldName
                );
                attachmentViewer.appendTo($("body"));
            } else {
                window.location =
                    "/web/content/" +
                    this.model +
                    "/" +
                    record.id +
                    "/" +
                    fieldName +
                    "/" +
                    record.name +
                    "?download=true";
            }
        },
    });

    field_registry.add("dms_preview", DocumentReader);

    return DocumentReader;
});
