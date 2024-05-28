# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DefaultCashEntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager.default"

    is_pos_cash = fields.Boolean(default=False)
