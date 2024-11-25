from odoo import _, api, exceptions, models


class CustomQueueJobChannel(models.Model):
    _inherit = "queue.job.channel"

    @api.constrains("parent_id", "name")
    def parent_required(self):
        for record in self:
            if record.name and not record.name.startswith("root") and not record.parent_id:
                raise exceptions.ValidationError(_("Parent channel required."))
        return
