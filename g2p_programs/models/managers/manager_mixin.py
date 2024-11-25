# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ManagerMixin(models.AbstractModel):
    """Manager mixin."""

    _name = "g2p.manager.mixin"
    _description = "Manager Mixin"

    manager_id = fields.Integer("Manager ID")
    manager_ref_id = fields.Reference(string="Manager", selection="_selection_manager_ref_id", required=True)

    @api.model
    def _selection_manager_ref_id(self):
        return []

    def open_manager_form(self):
        self.ensure_one()
        if self.manager_ref_id:
            # Get the res_model and res_id from the manager_ref_id (reference field)
            manager_ref_id = str(self.manager_ref_id)
            s = manager_ref_id.find("(")
            res_model = manager_ref_id[:s]
            res_id = self.manager_ref_id.id
            if res_id:
                action = self.env[res_model].get_formview_action()
                action.update(
                    {
                        "views": [(self.env[res_model].get_manager_view_id(), "form")],
                        "res_id": res_id,
                        "target": "new",
                        "context": self.env.context,
                        "flags": {"mode": "edit"},
                    }
                )
                return action

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "ERROR!",
                "message": "The Manager field must be filled-up.",
                "sticky": False,
                "type": "danger",
            },
        }
