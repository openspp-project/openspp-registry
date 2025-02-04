from odoo import fields, models


class SPPGRMTicketTag(models.Model):
    _name = "spp.grm.ticket.tag"
    _description = "Grievance Redress Mechanism Ticket Tag"

    name = fields.Char()
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
