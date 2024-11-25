from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        res = super().write(vals)

        pm_group = self.env.ref("g2p_programs.g2p_program_manager")
        admin_group = self.env.ref("g2p_registry_base.group_g2p_admin")
        contact_creation_group = self.env.ref("base.group_partner_manager")

        for user in self:
            if pm_group in user.groups_id and not (user._is_admin() or admin_group in user.groups_id):
                # getting recursion using orm
                # avoid recursion so directly sql injected
                self._cr.execute(
                    "DELETE FROM res_groups_users_rel WHERE uid = %s AND gid = %s",
                    (user.id, contact_creation_group.id),
                )
                user._invalidate_cache(["groups_id"])
        return res
