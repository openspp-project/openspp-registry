from odoo import api, fields, models


class OpenSPPEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    product_template_id = fields.Many2one(
        "product.template",
        compute="_compute_product_template_id",
        store=True,
        readonly=True,
    )

    voucher_redeemed = fields.Boolean(
        string="Voucher Redeemed",
        default=False,
        help="Check if the voucher has been redeemed.",
        readonly=True,
    )

    _sql_constraints = [
        (
            "product_template_unique",
            "UNIQUE(product_template_id)",
            "The product template must be unique across entitlement records.",
        ),
    ]

    is_pos_cash_entitlement = fields.Boolean(compute="_compute_is_pos_cash_entitlement")

    def _compute_is_pos_cash_entitlement(self):
        for rec in self:
            is_pos_cash_entitlement = False
            curr_entitlement_manager = self.env["g2p.program.entitlement.manager.default"].search(
                [("program_id", "=", rec.cycle_id.program_id.id), ("is_pos_cash", "=", True)]
            )
            if curr_entitlement_manager:
                is_pos_cash_entitlement = True

            rec.is_pos_cash_entitlement = is_pos_cash_entitlement

    @api.depends("state")
    def _compute_product_template_id(self):
        product_categ_id = self.env.ref("spp_pos.entitlement_product_categ").id
        product_categ_pos_id = self.env.ref("spp_pos.entitlement_product_categ_pos").id

        for rec in self:
            if rec.state != "approved" and rec.product_template_id:
                rec.product_template_id.unlink()
                rec.product_template_id = False
                continue

            if rec.state == "approved" and not rec.product_template_id:
                if product_template := self.env["product.template"].search(
                    [("name", "=", f"{rec.partner_id.name}: {rec.code}")]
                ):
                    rec.product_template_id = product_template[0]
                    product_template[0].entitlement_id = rec.id
                else:
                    rec.product_template_id = self.env["product.template"].create(
                        {
                            "name": f"{rec.partner_id.name}: {rec.code}",
                            "available_in_pos": True,
                            "list_price": rec.initial_amount * -1,
                            "is_locked": True,
                            "categ_id": product_categ_id,
                            "pos_categ_ids": [(4, product_categ_pos_id)],
                            "taxes_id": False,
                            "entitlement_id": rec.id,
                        }
                    )

    def unlink(self):
        for record in self:
            if record.product_template_id:
                record.product_template_id.unlink()
        return super().unlink()
