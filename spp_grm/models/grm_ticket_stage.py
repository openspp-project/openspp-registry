from odoo import api, fields, models


class SPPGRMTicketStage(models.Model):
    _name = "spp.grm.ticket.stage"
    _description = "Grievance Redress Mechanism Ticket Stage"
    _order = "sequence, id"

    name = fields.Char(string="Stage Name", required=True, translate=True)
    description = fields.Html(translate=True, sanitize_style=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    unattended = fields.Boolean()
    closed = fields.Boolean()
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
        domain=[("model", "=", "helpdesk.ticket")],
        help="If set an email will be sent to the " "customer when the ticket" "reaches this step.",
    )
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view " "when there are no records in that stage " "to display.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.onchange("closed")
    def _onchange_closed(self):
        if not self.closed:
            self.close_from_portal = False
