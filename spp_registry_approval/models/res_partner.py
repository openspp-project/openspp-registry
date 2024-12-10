from odoo import fields, models


class SppRegistry(models.Model):
    _inherit = "res.partner"

    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"

    state = fields.Selection(
        [
            (DRAFT, DRAFT.title()),
            (APPROVED, APPROVED.title()),
            (REJECTED, REJECTED.title()),
        ],
        string="State",
        default=DRAFT,
    )

    def approve_registry(self):
        for rec in self:
            if rec.user_has_groups("spp_registry_approval.approve_registry"):
                rec.sudo().state = self.APPROVED

    def reject_registry(self):
        for rec in self:
            if rec.user_has_groups("spp_registry_approval.reject_registry"):
                rec.sudo().state = self.REJECTED

    def reset_to_draft_registry(self):
        for rec in self:
            if rec.user_has_groups("spp_registry_approval.reset_to_draft_registry"):
                rec.sudo().state = self.DRAFT
