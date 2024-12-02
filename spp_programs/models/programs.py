# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class CustomG2PProgram(models.Model):
    _inherit = "g2p.program"

    is_one_time_distribution = fields.Boolean("One-time Distribution")

    view_id = fields.Many2one(
        "ir.ui.view",
        "Program UI Template",
        domain="[('model', '=', 'g2p.program'), " "('type', '=', 'form')," "('inherit_id', '=', False),]",
        default=lambda self: self._get_default_program_ui(),
    )

    def _get_default_program_ui(self):
        return self.env.ref("g2p_programs.view_program_list_form")

    def open_program_form(self):
        for rec in self:
            view_id = self.env.ref("g2p_programs.view_program_list_form")
            if rec.view_id:
                view_id = rec.view_id

            return {
                "type": "ir.actions.act_window",
                "res_model": "g2p.program",
                "view_mode": "form",
                "view_id": view_id.id,
                "res_id": rec.id,
                "target": "current",
            }

    def import_eligible_registrants(self, state="draft"):
        eligibility_managers = self.get_managers(self.MANAGER_ELIGIBILITY)
        if eligibility_managers:
            manager = eligibility_managers[0]

            new_beneficiaries_count = manager.import_eligible_registrants()

            if new_beneficiaries_count < 1000:
                message = _("%s Imported Beneficiaries") % new_beneficiaries_count
                kind = "success"
            else:
                message = _("Started importing %s beneficiaries") % new_beneficiaries_count
                kind = "warning"
        else:
            message = _("No Eligibility Manager defined.")
            kind = "danger"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
