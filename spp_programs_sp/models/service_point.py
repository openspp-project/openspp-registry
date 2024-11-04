from odoo import fields, models


class CustomOpenSPPServicePoint(models.Model):
    _inherit = "spp.service.point"

    g2p_entitlement_ids = fields.Many2many(
        comodel_name="g2p.entitlement",
        relation="g2p_entitlement_spp_service_point_rel",
        column1="spp_service_point_id",
        column2="g2p_entitlement_id",
        string="G2P Entitlements",
    )

    program_ids = fields.One2many(
        "g2p.program",
        compute="_compute_program_ids",
    )

    def _compute_program_ids(self):
        for rec in self:
            rec.program_ids = rec.g2p_entitlement_ids.mapped("program_id")
