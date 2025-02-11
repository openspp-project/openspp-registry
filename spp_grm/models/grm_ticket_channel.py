from odoo import fields, models


class SPPGRMTicketChannel(models.Model):
    _name = "spp.grm.ticket.channel"
    _description = "Grievance Redress Mechanism Ticket Channel"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(
        required=True,
        translate=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
