# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class DisableEditMixin(models.AbstractModel):
    """Disable Edit Mixin."""

    _name = "disable.edit.mixin"
    _description = "Disable Edit Option"

    DISABLE_EDIT_DOMAIN = []

    edit_css = fields.Html(
        sanitize=False,
        compute="_compute_css",
    )

    def _compute_css(self):
        # Add your dynamic computation logic here
        for rec in self:
            if rec.filtered_domain(self.DISABLE_EDIT_DOMAIN):
                rec.edit_css = "<style>.o_form_button_edit {display: none !important;}</style>"
            else:
                rec.edit_css = False
