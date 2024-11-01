from odoo import models


class DefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def new_cycle(self, name, new_start_date, sequence):
        default_attendance_type_id = self.env["spp.res.config.attendance.type"].search(
            [("set_as_default", "=", True)], limit=1
        )

        for rec in self:
            cycle = super(DefaultCycleManager, rec).new_cycle(name, new_start_date, sequence)
            cycle.write(
                {
                    "attendance_type_id": default_attendance_type_id.id,
                }
            )
            return cycle
