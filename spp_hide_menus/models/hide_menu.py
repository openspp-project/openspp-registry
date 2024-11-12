# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OpenSPPHideMenu(models.Model):
    _name = "spp.hide.menu"
    _description = "Hide Menu Configuration"

    name = fields.Many2one("ir.ui.menu", required=True)
    state = fields.Selection(
        [("show", "Show"), ("hide", "Hidden")],
        default="show",
    )
    default_groups_id = fields.Many2many("res.groups")

    def hide_menu(self, menu_id=None):
        record = self
        if menu_id:
            record = self.browse(menu_id)
        for rec in record:
            if rec.state == "show" and rec.name:
                show_non_openspp_group = [(6, 0, [self.env.ref("spp_hide_menus.show_non_openspp_menu_group").id])]
                rec.default_groups_id = rec.name.groups_id
                rec.name.write(
                    {
                        "groups_id": show_non_openspp_group,
                    }
                )
                rec.state = "hide"

    def show_menu(self):
        for rec in self:
            if rec.state == "hide" and rec.name:
                rec.name.groups_id = rec.default_groups_id
                rec.state = "show"
