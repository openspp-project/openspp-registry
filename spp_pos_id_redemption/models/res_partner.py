from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    draft_barcode = fields.Char(compute="_compute_draft_barcode")

    @api.depends("reg_ids")
    def _compute_draft_barcode(self):
        for rec in self:
            draft_barcode = ""
            if rec.is_registrant and rec.reg_ids:
                draft_barcode = rec.reg_ids.mapped("value")

            rec.draft_barcode = draft_barcode
            rec.barcode = draft_barcode
