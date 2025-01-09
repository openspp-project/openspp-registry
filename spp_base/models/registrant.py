# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OpenSPPResPartner(models.Model):
    _inherit = "res.partner"

    tags_ids = fields.Many2many("g2p.registrant.tags", string="Registrant Tags")
    kind_as_str = fields.Char(related="kind.name", string="String Kind")
    gender = fields.Many2one("gender.type", ondelete="restrict")
