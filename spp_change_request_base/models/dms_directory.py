from odoo import fields, models


class SPPDMSDirectoryCustom(models.Model):
    _inherit = "spp.dms.directory"

    change_request_id = fields.Many2one("spp.change.request", "Change Request")
