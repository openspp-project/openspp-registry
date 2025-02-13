# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    # Tag-based Eligibility Manager
    eligibility_kind = fields.Selection(selection_add=[("tags_eligibility", "Tag-based Eligibility")])
    tags_id = fields.Many2one("g2p.registrant.tags", string="Tags")
    area_id = fields.Many2one(
        "spp.area",
        domain=lambda self: [("kind", "=", self.env.ref("spp_area_base.admin_area_kind").id)],
    )
    custom_domain = fields.Text(string="Tags Domain", default="[]", readonly=True)

    @api.onchange("tags_id", "area_id")
    def on_tags_area_change(self):
        custom_domain = []
        if self.tags_id:
            custom_domain.append(("tags_ids", "=", self.tags_id.id))

        if self.area_id:
            custom_domain.append(("area_id", "=", self.area_id.id))

        self.custom_domain = json.dumps(custom_domain)

    def _check_required_fields(self):
        super()._check_required_fields()
        if self.eligibility_kind == "tags_eligibility":
            if not self.tags_id:
                raise UserError(_("A tag is needed for this eligibility criteria type."))
        return

    def get_manager_tags_val(self, program_id):
        return {
            "name": "Tags Manager",
            "program_id": program_id,
            "tags_id": self.tags_id.id,
            "area_id": self.area_id.id,
        }

    def _get_eligibility_manager(self, program_id):
        res = super()._get_eligibility_manager(program_id)
        if self.eligibility_kind == "tags_eligibility":
            # Add a new record to tag-base eligibility manager model
            manager_tags_val = self.get_manager_tags_val(program_id)
            def_mgr = self.env["g2p.program_membership.manager.tags"].create(manager_tags_val)

            # Add a new record to eligibility manager parent model
            eligibility_manager_val = self._get_eligibility_managers_val(program_id, def_mgr)
            mgr = self.env["g2p.eligibility.manager"].create(eligibility_manager_val)
            res = {"eligibility_managers": [(4, mgr.id)]}
        return res
