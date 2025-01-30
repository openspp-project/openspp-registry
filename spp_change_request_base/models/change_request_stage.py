# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ChangeRequestValidationStages(models.Model):
    _name = "spp.change.request.validation.stage"
    _description = "Change Request Validation Stage"
    _order = "id"

    name = fields.Char("Stage")
