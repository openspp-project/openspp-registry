# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RejectChangeRequestWiz(models.TransientModel):
    _name = "spp.change.request.reject.wizard"
    _description = "Change Request Rejection Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("change_request_id"):
            res["change_request_id"] = self.env.context["change_request_id"]
        else:
            if self.env.context.get("active_id"):
                res["change_request_id"] = self.env.context["active_id"]
        return res

    change_request_id = fields.Many2one("spp.change.request", "Change Request", required=True)
    rejected_by_id = fields.Many2one("res.users", "Rejected by", default=lambda self: self.env.user.id)
    rejected_remarks = fields.Text("Rejection Remarks", required=True)
    dialog_message = fields.Text(compute="_compute_message")

    def reject_change_request(self):
        for rec in self:
            if rec.change_request_id:
                rec.change_request_id.request_type_ref_id._on_reject(rec.change_request_id, rec.rejected_remarks)
            else:
                raise UserError(_("There are no change request selected."))

    @api.depends("change_request_id")
    def _compute_message(self):
        for rec in self:
            msg = _(
                "Are you sure you would like to reject this request: %s",
                rec.change_request_id.name,
            )
            rec.dialog_message = msg
