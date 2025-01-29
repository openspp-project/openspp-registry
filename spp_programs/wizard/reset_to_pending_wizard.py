# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResetPendingEntitlementWiz(models.TransientModel):
    _name = "spp.reset.pending.entitlement.wizard"
    _description = "Reset to Pending Entitlement Wizard"

    def entitlement_state_to_add(self):
        return ["reject"]

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            entitlement_ids = []

            for rec in self.env.context.get("active_ids"):
                entitlement = self.env["g2p.entitlement"].search(
                    [
                        ("id", "=", rec),
                    ]
                )
                if entitlement.state in self.entitlement_state_to_add():
                    entitlement_ids.append([0, 0, {"entitlement_id": rec}])

            res["entitlement_ids"] = entitlement_ids

        return res

    entitlement_ids = fields.One2many(
        "spp.entitlement.reset.pending",
        "wizard_id",
        string="Entitlements",
        required=True,
    )

    def reset_to_pending(self):
        if self.entitlement_ids:
            return self.entitlement_ids.entitlement_id._reset_to_pending()

    def open_wizard(self):
        _logger.info("Entitlement IDs: %s" % self.env.context.get("active_ids"))
        return {
            "name": "Reset to Pending Entitlement",
            "view_mode": "form",
            "res_model": "spp.reset.pending.entitlement.wizard",
            "view_id": self.env.ref("spp_programs.reset_to_pending_entitlement_wizard").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "nodestroy": True,
            "context": self.env.context,
        }

    def close_wizard(self):
        return {"type": "ir.actions.act_window_close"}


class SPPEntitlementResetPending(models.TransientModel):
    _name = "spp.entitlement.reset.pending"
    _description = "Multi Entitlement Reset to Pending"

    entitlement_id = fields.Many2one(
        "g2p.entitlement",
        "Entitlement",
        help="A Entitlement",
        required=True,
    )
    cycle_id = fields.Many2one(
        "g2p.cycle",
        "Cycle",
        help="A Cycle",
        related="entitlement_id.cycle_id",
    )
    wizard_id = fields.Many2one(
        "spp.reset.pending.entitlement.wizard",
        "Reset to Pending Entitlement Wizard",
        help="A Wizard",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        related="entitlement_id.partner_id",
    )
    code = fields.Char(related="entitlement_id.code")
    currency_id = fields.Many2one("res.currency", readonly=True, related="entitlement_id.journal_id.currency_id")
    initial_amount = fields.Monetary(
        required=True,
        currency_field="currency_id",
        related="entitlement_id.initial_amount",
        readonly=False,
    )
