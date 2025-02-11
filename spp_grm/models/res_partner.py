from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    grm_ticket_ids = fields.One2many(
        comodel_name="spp.grm.ticket",
        inverse_name="partner_id",
        string="Related Tickets",
    )

    grm_ticket_count = fields.Integer(compute="_compute_grm_ticket_count", string="Ticket Count")

    grm_ticket_active_count = fields.Integer(compute="_compute_grm_ticket_count", string="Active Ticket Count")

    grm_ticket_count_string = fields.Char(compute="_compute_grm_ticket_count", string="Tickets")

    def _compute_grm_ticket_count(self):
        for record in self:
            ticket_ids = self.env["spp.grm.ticket"].search([("partner_id", "child_of", record.id)])
            record.grm_ticket_count = len(ticket_ids)
            record.grm_ticket_active_count = len(ticket_ids.filtered(lambda ticket: not ticket.stage_id.closed))
            count_active = record.grm_ticket_active_count
            count = record.grm_ticket_count
            record.grm_ticket_count_string = f"{count_active} / {count}"

    def action_view_grm_tickets(self):
        return {
            "name": "Tickets",  # self.name,
            "view_mode": "tree,form",
            "res_model": "spp.grm.ticket",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            "context": self.env.context,
        }
