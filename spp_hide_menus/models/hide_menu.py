# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OpenSPPIDPass(models.Model):
    _name = "spp.hide.menu"
    _description = "Hide Menu Configuration"

    name = fields.Many2one("ir.ui.menu")
    state = fields.Selection(
        [("show", "Show"), ("hide", "Hidden")],
        default="show",
    )
    default_groups_id = fields.Many2many("res.groups")

    def hide_menu(self):
        for rec in self:
            if rec.state == "show":
                show_non_openspp = [(5, self.env.ref('spp_hide_menus.show_non_openspp_menu_group'))]
                rec.state = "hide"
