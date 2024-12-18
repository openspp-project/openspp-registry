from odoo import api, fields, models


class InheritG2PMultiEntitlementApprovalWiz(models.TransientModel):
    _inherit = "g2p.multi.entitlement.approval.wizard"

    number_of_beneficiaries = fields.Integer(
        compute="_compute_number_of_beneficiaries",
        string="Number of Beneficiaries",
    )

    @api.depends("entitlement_ids")
    def _compute_number_of_beneficiaries(self):
        self.number_of_beneficiaries = len(self.entitlement_ids)
