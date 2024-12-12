from odoo import SUPERUSER_ID, _, api, fields, models


class G2PEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    state = fields.Selection(
        selection_add=[("reject", "Rejected")],
    )

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        # to bypass the validation in g2p_programs/models/entitlement.py
        if not self.env.user.has_group("g2p_registry_base.group_g2p_admin"):
            other_user = self.env["res.users"].browse(SUPERUSER_ID)
            self = self.with_user(other_user)

        arch, view = super()._get_view(view_id, view_type, **options)

        return arch, view

    def reject_entitlement(self):
        if self.env.user.has_group("spp_programs.approve_entitlement"):
            for rec in self.sudo():
                rec.state = "reject"

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
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Entitlement"),
                    "message": "You are not authorized to reject entitlement",
                    "sticky": False,
                    "type": "danger",
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

    def approve_entitlement(self):
        if self.env.user.has_group("spp_programs.approve_entitlement"):
            super(G2PEntitlement, self.sudo()).approve_entitlement()
        super().approve_entitlement()
