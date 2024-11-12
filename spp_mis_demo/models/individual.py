# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PIndividual(models.Model):
    _inherit = "res.partner"

    z_cst_indv_medical_condition = fields.Integer("chronic illness/medical conditions level")  # 0-100
    z_cst_indv_disability_level = fields.Integer("Disability level")  # 0-100
    z_cst_indv_pregnancy_start = fields.Date("Pregnancy start")  # We set a date to be able to clean it later
    z_cst_indv_lactation_start = fields.Date("Lactation start")  # We set a date to be able to clean it later
