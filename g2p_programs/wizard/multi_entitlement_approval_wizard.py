# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class G2PMultiEntitlementApprovalWiz(models.TransientModel):
    _name = "g2p.multi.entitlement.approval.wizard"
    _description = "Multi Entitlement Approval Wizard"

    @api.model
    def default_get(self, fields):
        _logger.info(
            "Adding to Multi Entitlement Approval Wizard with IDs: %s" % self.env.context.get("active_ids")
        )
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            entitlement_ids = []
            cycle_id = 0
            for rec in self.env.context.get("active_ids"):
                entitlement = self.env["g2p.entitlement"].search(
                    [
                        ("id", "=", rec),
                    ]
                )
                if entitlement.state in ("draft", "pending_validation"):
                    entitlement_ids.append([0, 0, {"entitlement_id": rec}])

                cycle_id = entitlement.cycle_id.id

            cycle = self.env["g2p.cycle"].search(
                [
                    ("id", "=", cycle_id),
                ]
            )
            if cycle:
                if cycle.state == "approved":
                    res["cycle_id"] = cycle_id
            res["entitlement_ids"] = entitlement_ids

        return res

    entitlement_ids = fields.One2many(
        "g2p.multi.entitlement.approval",
        "wizard_id",
        string="Entitlements",
        required=True,
    )
    cycle_id = fields.Many2one(
        "g2p.cycle",
        "Cycle",
        help="A Cycle",
    )

    def approve_entitlements(self):
        if self.entitlement_ids:
            return self.entitlement_ids.entitlement_id.approve_entitlement()

    def open_wizard(self):
        _logger.info("Entitlement IDs: %s" % self.env.context.get("active_ids"))
        return {
            "name": "Multiple Entitlements Approval",
            "view_mode": "form",
            "res_model": "g2p.multi.entitlement.approval.wizard",
            "view_id": self.env.ref("g2p_programs.multi_entitlement_approval_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "nodestroy": True,
            "context": self.env.context,
        }

    def close_wizard(self):
        return {"type": "ir.actions.act_window_close"}


class G2PMultiEntitlementApproval(models.TransientModel):
    _name = "g2p.multi.entitlement.approval"
    _description = "Multi Entitlement Approval"

    entitlement_id = fields.Many2one(
        "g2p.entitlement",
        "Entitlement",
        help="A Entitlement",
        required=True,
    )
    wizard_id = fields.Many2one(
        "g2p.multi.entitlement.approval.wizard",
        "Multi Entitlement Approval Wizard",
        help="A Wizard",
        required=True,
    )
    cycle_id = fields.Many2one(
        "g2p.cycle",
        "Cycle",
        help="A Cycle",
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        related="entitlement_id.partner_id",
    )
    code = fields.Char(related="entitlement_id.code")
    currency_id = fields.Many2one(
        "res.currency", readonly=True, related="entitlement_id.journal_id.currency_id"
    )
    initial_amount = fields.Monetary(
        required=True,
        currency_field="currency_id",
        related="entitlement_id.initial_amount",
        readonly=False,
    )
    state = fields.Selection(
        [
            ("New", "New"),
            ("Okay", "Okay"),
            ("Conflict", "Conflict"),
            ("Approved", "Approved"),
        ],
        "Status",
        readonly=True,
        default="New",
    )
