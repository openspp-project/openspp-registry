from odoo import _, fields, models
from odoo.exceptions import UserError


class G2PGroupMembership(models.Model):
    _inherit = "g2p.group.membership"

    individual_gender = fields.Many2one("gender.type", related="individual.gender", readonly=True)

    def unlink(self):
        for rec in self:
            group_id = rec.group
            res = super(G2PGroupMembership, rec).unlink()
            if (
                self.env.ref("g2p_registry_membership.group_membership_kind_head").id
                not in group_id.group_membership_ids.mapped("kind").ids
            ):
                raise UserError(_("Farm must have a head member."))
            return res
