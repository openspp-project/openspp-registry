from odoo import fields, models


class SPPDMSDirectoryCustom(models.Model):
    _inherit = "spp.dms.directory"

    change_request_edit_farmer_id = fields.Many2one("spp.change.request.edit.farmer", "Change request")


class SPPDMSFileCustom(models.Model):
    _inherit = "spp.dms.file"

    change_request_edit_farmer_id = fields.Many2one("spp.change.request.edit.farmer", "Change request")
