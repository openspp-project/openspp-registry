# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, api, fields, models

_logger = logging.getLogger(__name__)


class ChangeRequestValidationSequenceMixin(models.AbstractModel):
    """Change Request Validation Sequence mixin."""

    _name = "spp.change.request.validation.sequence.mixin"
    _description = "Change Request Validation Sequence Mixin"

    @api.model
    def _default_validation_ids(self):
        _logger.debug("DEBUG! _default_validation_ids: %s", self._name)
        validations = self.env["spp.change.request.validation.sequence"].search([("request_type", "=", self._name)])
        if validations:
            validation_ids = []
            for rec in validations:
                validation_ids.append(Command.link(rec.id))
            _logger.debug("DEBUG! _default_validation_ids: validation_ids: %s", validation_ids)
            return validation_ids
        else:
            return None

    validation_ids = fields.Many2many(
        "spp.change.request.validation.sequence",
        relation="spp_change_request_rel",
        string="Validation Sequence",
        default=_default_validation_ids,
        required=True,
    )
