from odoo import SUPERUSER_ID, _, api, fields, models


class G2PEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    state = fields.Selection(
        selection_add=[("reject", "Rejected")],
    )
    date_rejected = fields.Date()
    rejected_reason = fields.Text(string="Rejected Reason")

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        # to bypass the validation in g2p_programs/models/entitlement.py
        if not self.env.user.has_group("g2p_registry_base.group_g2p_admin"):
            other_user = self.env["res.users"].browse(SUPERUSER_ID)
            self = self.with_user(other_user)

        arch, view = super()._get_view(view_id, view_type, **options)

        return arch, view

    def reject_entitlement(self):
        form_id = self.env.ref("spp_programs.reject_entitlement_wizard").id
        action = {
            "name": _("Reject Entitlement"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.reject.entitlement.wizard",
            "target": "new",
            "context": {
                "to_state": "reject",
            },
        }
        return action

    @staticmethod
    def allowed_to_reject_entitlement():
        return ["draft", "pending_validation"]

    def _reject_entitlement(self, to_state="reject", reject_reason=""):
        for rec in self.sudo():
            if rec.state not in self.allowed_to_reject_entitlement():
                continue
            rec.state = to_state
            rec.rejected_reason = reject_reason
            rec.date_rejected = fields.Date.today()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Entitlement"),
                "message": "Entitlement Rejected",
                "sticky": False,
                "type": "danger",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def approve_entitlement(self):
        if self.env.user.has_group("spp_programs.approve_entitlement"):
            return super(G2PEntitlement, self.sudo()).approve_entitlement()
        return super().approve_entitlement()

    def write(self, vals):
        if self.env.user.has_group("spp_programs.approve_entitlement") or self.env.user.has_group(
            "spp_programs.approve_entitlement"
        ):
            return super(G2PEntitlement, self.sudo()).write(vals)
        return super().write(vals)

    def reset_to_pending(self):
        form_id = self.env.ref("spp_programs.reset_to_pending_entitlement_wizard").id
        action = {
            "name": _("Reset to Pending Entitlement"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.reset.pending.entitlement.wizard",
            "target": "new",
        }
        return action

    def _reset_to_pending(self):
        for rec in self.sudo():
            rec.state = "pending_validation"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Entitlement"),
                "message": "Entitlement Rejected",
                "sticky": False,
                "type": "success",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
