# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CancelChangeRequestWiz(models.TransientModel):
    _name = "spp.change.request.cancel.wizard"
    _description = "Change Request Cancel Wizard"

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
    cancelled_by_id = fields.Many2one("res.users", "Cancelled by", default=lambda self: self.env.user.id)
    dialog_message = fields.Text(compute="_compute_message")

    def cancel_change_request(self):
        for rec in self:
            if rec.change_request_id:
                if rec.change_request_id.request_type_ref_id:
                    rec.change_request_id.request_type_ref_id._cancel(rec.change_request_id)
                else:
                    rec.change_request_id._cancel(rec.change_request_id)
            else:
                raise UserError(_("There are no change request selected."))

    @api.depends("change_request_id")
    def _compute_message(self):
        for rec in self:
            msg = _(
                "Are you sure you would like to cancel this request: %s",
                rec.change_request_id.name,
            )
            rec.dialog_message = msg
