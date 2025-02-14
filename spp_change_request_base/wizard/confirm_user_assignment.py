# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ConfirmUserAssignmentWiz(models.TransientModel):
    _name = "spp.change.request.user.assign.wizard"
    _description = "Change Request User Assignment Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("change_request_id"):
            res["change_request_id"] = self.env.context["change_request_id"]
        else:
            if self.env.context.get("active_id"):
                res["change_request_id"] = self.env.context["active_id"]
        if self.env.context.get("curr_assign_to_id"):
            if self.env.context["curr_assign_to_id"] != self.env.user.id:
                res["assign_to_id"] = self.env.user
            res["curr_assign_to_id"] = self.env.context["curr_assign_to_id"]
        else:
            res["assign_to_id"] = self.env.user.id

        if self.env.context.get("assign_to"):
            res["assign_to"] = self.env.context["assign_to"]
        return res

    change_request_id = fields.Many2one("spp.change.request", "Change Request", required=True)
    curr_assign_to_id = fields.Many2one("res.users", "Currently Assigned to", related="change_request_id.assign_to_id")
    assign_to_id = fields.Many2one("res.users", "User")
    assign_to_id_domain = fields.Char(
        compute="_compute_assign_to_id_domain",
    )
    dialog_message = fields.Text(compute="_compute_message_assignment")
    assign_to_any = fields.Boolean(compute="_compute_message_assignment")
    assign_to = fields.Boolean(default=False)

    def assign_to_user(self):
        """
        Assign the change request to the user.
        """
        for rec in self:
            rec.change_request_id.assign_to_user(rec.assign_to_id)

    @api.depends("change_request_id", "assign_to_id")
    def _compute_message_assignment(self):
        """
        Compute the dialog_message and assign_to_any fields.
        """
        for rec in self:
            msg1 = _("Assign this change request to:")
            assign_to_any = True
            rec.update(
                {
                    "dialog_message": f"{msg1}",
                    "assign_to_any": assign_to_any,
                }
            )

    @api.depends("assign_to_id")
    def _compute_assign_to_id_domain(self):
        """
        Compute the assign_to_id_domain field.

        This method is used to filter the users based on the group ids.
        """
        group_ids = self._get_group_ids()

        user_group_ids = self.env.user.groups_id.ids

        same_group_ids = list(set(user_group_ids).intersection(group_ids))
        domain = [("groups_id", "in", same_group_ids)]

        for rec in self:
            rec.assign_to_id_domain = json.dumps(domain)

    def _get_group_ids(self):
        """
        Get the group ids for the user.
        Override this method in the implementation-specific module to specify the group ids to be checked.

        :return: List of group ids.
        """
        return []
