from odoo import fields, models


class Farmer(models.Model):
    _inherit = "res.partner"

    experience_years = fields.Integer(string="Years of Experience")
    formal_agricultural_training = fields.Boolean("Do you have formal training in agriculture?")
    farmer_national_id = fields.Char(string="National ID Number")
    farmer_household_size = fields.Integer()
    farmer_postal_address = fields.Char("Postal Address")
    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("widowed", "Widowed"),
            ("married", "Married"),
            ("separated", "Separated"),
        ],
    )
    highest_education_level = fields.Selection(
        [
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("tertiary", "Tertiary"),
        ],
        string="Highest Educational Level",
    )


class TempFarmer(models.Model):
    _name = "spp.farmer"
    _description = "Temporary Model for Farmer"

    def _get_dynamic_selection(self):
        options = self.env["gender.type"].search([])
        return [(option.value, option.code) for option in options]

    farmer_family_name = fields.Char()
    farmer_given_name = fields.Char()
    farmer_addtnl_name = fields.Char(string="Farmer Additional Name")
    farmer_national_id = fields.Char(string="National ID Number")
    farmer_mobile_tel = fields.Char(string="Mobile Telephone Number")
    farmer_sex = fields.Selection(selection=_get_dynamic_selection, string="Sex")
    farmer_birthdate = fields.Date("Farmer Date of Birth")
    farmer_household_size = fields.Char()
    farmer_postal_address = fields.Char("Postal Address")
    farmer_email = fields.Char("E-mail Address")
    farmer_formal_agricultural = fields.Boolean()
    farmer_highest_education_level = fields.Selection(
        [
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("tertiary", "Tertiary"),
        ],
        string="Farmer Highest Educational Level",
    )
    farmer_marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("widowed", "Widowed"),
            ("separated", "Separated"),
        ]
    )
    farmer_individual_id = fields.Many2one("res.partner")
