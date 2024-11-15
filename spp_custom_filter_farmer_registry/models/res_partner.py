from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "custom.filter.mixin"]

    tags_ids = fields.Many2many("g2p.registrant.tags", allow_filter=True)
    farmer_national_id = fields.Char(allow_filter=True)
    farmer_postal_address = fields.Char(allow_filter=True)
    marital_status = fields.Selection(allow_filter=True)
    highest_education_level = fields.Selection(allow_filter=True)
    household_size = fields.Integer(allow_filter=True)
    z_cst_indv_medical_condition = fields.Integer(allow_filter=True)
    z_ind_grp_is_single_head_hh = fields.Boolean(allow_filter=True)
    z_ind_grp_is_hh_with_medical_condition = fields.Boolean(allow_filter=True)
    z_ind_grp_is_hh_with_children = fields.Boolean(allow_filter=True)
