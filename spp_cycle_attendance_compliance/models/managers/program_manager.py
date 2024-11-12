from odoo import models


class DefaultProgramManager(models.Model):
    _inherit = "g2p.program.manager.default"

    def new_cycle(self):
        cycle_id = super().new_cycle()
        if cycle_id.program_id.target_type == "group":
            for cycle_membership_id in cycle_id.cycle_membership_ids:
                for member in cycle_membership_id.partner_id.group_membership_ids.mapped("individual"):
                    self.env["spp.cycle.group.membership.attendance"].create(
                        {
                            "cycle_membership_id": cycle_membership_id.id,
                            "individual_id": member.id,
                        }
                    )
        return cycle_id
