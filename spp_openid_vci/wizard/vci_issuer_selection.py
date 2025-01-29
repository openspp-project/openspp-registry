from odoo import fields, models


class IssueCardWiz(models.TransientModel):
    _name = "spp.issue.card.wizard"

    issuer_id = fields.Many2one("g2p.openid.vci.issuers", "Issuer", required=True)

    def issue_card(self):
        partner_ids = self.env["res.partner"].search([("id", "in", self.env.context.get("active_ids"))])
        return partner_ids._issue_vc_qr(self.issuer_id)
