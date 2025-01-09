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

    voucher_redeemed = fields.Boolean(related="entitlement_id.voucher_redeemed", store=True, readonly=True)

    cycle_id = fields.Many2one(related="entitlement_id.cycle_id", store=True)
    cycle_id_str = fields.Char(related="cycle_id.name", store=True)

    program_id = fields.Many2one(related="cycle_id.program_id", store=True)
    program_id_str = fields.Char(related="program_id.name", store=True)
    entitlement_valid_until = fields.Date(related="entitlement_id.valid_until", store=True)

    _sql_constraints = [
        (
            "entitlement_id_unique",
            "UNIQUE(entitlement_id)",
            "The entitlement must be unique across product template records.",
        ),
    ]

    @api.depends("cycle_id")
    def _compute_program_id(self):
        for rec in self:
            program_id = None
            if rec.cycle_id:
                program_id = rec.cycle_id.program_id.id

            rec.program_id = program_id

    @api.depends("entitlement_id")
    def _compute_created_from_entitlement(self):
        for rec in self:
            rec.created_from_entitlement = bool(rec.entitlement_id)

    def redeem_voucher(self):
        for rec in self:
            if rec.entitlement_id:
                rec.entitlement_id.voucher_redeemed = True

    def unredeem_voucher(self):
        for rec in self:
            if rec.entitlement_id:
                rec.entitlement_id.voucher_redeemed = False
