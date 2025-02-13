# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPDefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    @api.model
    def _get_admin_area_domain(self):
        return [("kind", "=", self.env.ref("spp_area_base.admin_area_kind").id)]

    admin_area_ids = fields.Many2many("spp.area", domain=_get_admin_area_domain)
    target_type = fields.Selection(related="program_id.target_type")

    @api.onchange("admin_area_ids")
    def on_admin_area_ids_change(self):
        eligibility_domain = "[]"
        if self.admin_area_ids:
            area_ids = self.admin_area_ids.ids
            eligibility_domain = f"[('area_id', 'in', ({area_ids}))]"

        self.eligibility_domain = eligibility_domain

    def _prepare_eligible_domain(self, membership=None):
        domain = super()._prepare_eligible_domain(membership)

        domain += [("is_registrant", "=", True)]

        return domain
