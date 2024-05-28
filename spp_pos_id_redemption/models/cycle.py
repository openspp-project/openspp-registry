from odoo import api, fields, models


class OpenSPPEntitlement(models.Model):
    _inherit = "g2p.cycle"

    is_pos_cash_entitlement = fields.Boolean(compute="_compute_is_pos_cash_entitlement")

    def _compute_is_pos_cash_entitlement(self):
        for rec in self:
            is_pos_cash_entitlement = False
            curr_entitlement_manager = self.env["g2p.program.entitlement.manager.default"].search(
                [("program_id", "=", rec.program_id.id), ("is_pos_cash", "=", True)]
            )
            if curr_entitlement_manager:
                is_pos_cash_entitlement = True

            rec.is_pos_cash_entitlement = is_pos_cash_entitlement
