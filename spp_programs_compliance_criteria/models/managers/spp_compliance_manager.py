from odoo import api, fields, models


class SppComplianceManager(models.Model):
    _name = "spp.compliance.manager"
    _inherit = ["g2p.manager.mixin"]
    _description = "Compliance Criteria Manager"

    program_id = fields.Many2one(
        comodel_name="g2p.program",
        string="Program",
        required=True,
        auto_join=True,
        ondelete="cascade",
        readonly=True,
    )

    @api.model
    def _selection_manager_ref_id(self):
        res = super()._selection_manager_ref_id()
        for item in [
            ("g2p.program_membership.manager.default", "Default Manager"),
        ]:
            if item not in res:
                res.append(item)
        return res
