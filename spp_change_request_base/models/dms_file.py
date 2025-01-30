import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class SPPDMSFileCustom(models.Model):
    _inherit = "spp.dms.file"

    change_request_id = fields.Many2one("spp.change.request", "Change Request")

    def create(self, vals):
        # _logger.info("DEBUG vals: %s", vals)
        return super().create(vals)

    def action_save_and_close(self):
        return {"type": "ir.actions.act_window_close"}

    def action_close(self):
        return {"type": "ir.actions.act_window_close"}

    def action_attach_documents(self):
        for rec in self:
            form_id = self.env.ref("spp_change_request.view_dms_file_spp_custom_form").id
            action = {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_id": form_id,
                "view_type": "form",
                "res_model": "spp.dms.file",
                "target": "new",
                "res_id": rec.id,
            }
            dms_context = {
                "category_readonly": True,
            }
            action.update(
                {
                    "name": _("Upload Document: %s", rec.category_id.name),
                    "context": dms_context,
                }
            )
            return action
