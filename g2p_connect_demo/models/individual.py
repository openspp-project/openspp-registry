# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    # Fields from G2PIndividual
    z_cst_indv_cyclone_aug_2022_injured = fields.Boolean("Injured during Cyclone Aug 2022")
    z_cst_indv_disability_level = fields.Integer("Disability level")  # 0-100
    z_cst_indv_receive_government_benefits = fields.Boolean("Receive government benefits")
    z_cst_indv_cyclone_aug_2022_lost_livestock = fields.Boolean("Lost significant livestock during Cyclone Aug 2022")
    z_cst_indv_cyclone_aug_2022_lost_primary_source_income = fields.Boolean(
        "Lost primary source income during Cyclone Aug 2022"
    )
    z_cst_indv_has_birth_certificate = fields.Boolean("Has birth certificate")

    # Fields from G2PRegistrant
    full_address = fields.Text(compute="_compute_address")

    @api.depends("street", "street2", "city", "zip")
    def _compute_address(self):
        for rec in self:
            full_address = ""
            if rec.street:
                full_address = rec.street
            if rec.street2:
                full_address += f" {rec.street2}"
            if rec.city:
                full_address += f" {rec.city}"
            if rec.zip:
                full_address += f" {rec.zip}"
            rec.full_address = full_address
