# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RegistryCRCustom(models.Model):
    """
    Extends the res.partner model to link the change requests to the group registrants.
    Filter applied and cancelled change requests only
    """

    _inherit = "res.partner"

    change_request_ids = fields.One2many("spp.change.request", "registrant_id", "Change Requests")
