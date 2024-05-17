from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    entitlement_id = fields.Many2one(
        "g2p.entitlement",
    )
    entitlement_partner_id = fields.Many2one(
        related="entitlement_id.partner_id",
        store=True,
    )
    created_from_entitlement = fields.Boolean(compute="_compute_created_from_entitlement", store=True)

    _sql_constraints = [
        (
            "entitlement_id_unique",
            "UNIQUE(entitlement_id)",
            "The entitlement must be unique across product template records.",
        ),
    ]

    @api.depends("entitlement_id")
    def _compute_created_from_entitlement(self):
        for rec in self:
            rec.created_from_entitlement = bool(rec.entitlement_id)
