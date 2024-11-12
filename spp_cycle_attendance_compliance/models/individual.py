from odoo import api, fields, models


class SPPIndividualCustom(models.Model):
    _inherit = "res.partner"

    personal_identifier = fields.Char(
        compute="_compute_personal_identifier",
        store=True,
    )

    @api.depends("reg_ids")
    def _compute_personal_identifier(self):
        for rec in self:
            for reg_id in rec.reg_ids:
                if reg_id.value and reg_id.id_type and reg_id.id_type.name:
                    rec.personal_identifier = reg_id.value
