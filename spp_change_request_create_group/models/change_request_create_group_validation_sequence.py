from odoo import api, models


class ChangeRequestCreateGroupValidationSequence(models.Model):
    _inherit = "spp.change.request.validation.sequence"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.create.group", "Create Group")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection
