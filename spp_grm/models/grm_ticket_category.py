from odoo import fields, models


class SPPGRMCategory(models.Model):
    _name = "spp.grm.ticket.category"
    _description = "Grievance Redress Mechanism Ticket Category"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(
        default=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
