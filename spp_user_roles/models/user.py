# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import Command, api, fields, models


class ResUsersCustomSPP(models.Model):
    _inherit = "res.users"

    center_area_ids = fields.Many2many(
        comodel_name="spp.area",
        string="Center Areas",
        compute="_compute_center_area_ids",
        store=True,
    )

    @api.depends("role_line_ids.role_id")
    def _compute_center_area_ids(self):
        for user in self:
            if user.center_area_ids:
                user.update({"center_area_ids": [Command.clear()]})
            if user.role_line_ids:
                center_area_ids = []
                for rl in user.role_line_ids.filtered(lambda a: a.role_type == "local"):
                    if rl.local_area_id:
                        center_area_ids.append(Command.link(rl.local_area_id.id))
                if center_area_ids:
                    user.update({"center_area_ids": center_area_ids})

    @api.model
    def _default_role_lines(self):
        default_user = self.env.ref("base.default_user", raise_if_not_found=False)
        default_values = []
        if default_user:
            for role_line in default_user.with_context(active_test=False).role_line_ids:
                default_values.append(
                    {
                        "role_id": role_line.role_id.id,
                        "date_from": role_line.date_from,
                        "date_to": role_line.date_to,
                        "is_enabled": role_line.is_enabled,
                        "local_area_id": role_line.local_area_id.id,
                    }
                )
        return default_values

    def set_groups_from_roles(self, force=False):
        """Override the original method to exclude some groups in removing."""
        DO_NOT_REMOVE_GROUPS = [
            self.env.ref("base.group_user").id,
            self.env.ref("base.group_no_one").id,
            self.env.ref("mail.group_mail_template_editor").id,
            self.env.ref("base.group_portal").id,
            self.env.ref("base.group_public").id,
        ]
        role_groups = {}
        # We obtain all the groups associated to each role first, so that
        # it is faster to compare later with each user's groups.
        for role in self.mapped("role_line_ids.role_id"):
            role_groups[role] = list(set(role.group_id.ids + role.implied_ids.ids + role.trans_implied_ids.ids))

        for user in self:
            if not user.role_line_ids and not force:
                continue
            group_ids = []
            for role_line in user._get_enabled_roles():
                role = role_line.role_id
                group_ids += role_groups[role]
            group_ids = list(set(group_ids))  # Remove duplicates IDs
            groups_to_add = list(set(group_ids) - set(user.groups_id.ids))
            groups_to_remove = list(set(user.groups_id.ids) - set(group_ids))

            for group in DO_NOT_REMOVE_GROUPS:
                if group in groups_to_remove:
                    groups_to_remove.remove(group)

            to_add = [(4, gr) for gr in groups_to_add]
            to_remove = [(3, gr) for gr in groups_to_remove]
            groups = to_remove + to_add
            if groups:
                vals = {"groups_id": groups}
                super(ResUsersCustomSPP, user).write(vals)
        return True
