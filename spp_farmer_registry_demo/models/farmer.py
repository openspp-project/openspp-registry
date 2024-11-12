from odoo import fields, models


class Farmer(models.Model):
    _inherit = "res.partner"

    marital_status = fields.Selection(
        selection_add=[
            ("married_monogamous", "Married Monogamous"),
            ("married_polygamous", "Married Polygamous"),
        ]
    )
    highest_education_level = fields.Selection(
        selection_add=[
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("certificate", "Certificate"),
            ("diploma", "Diploma"),
            ("university", "University"),
            ("tertiary", "Tertiary"),
        ],
    )


class TempFarmer(models.Model):
    _inherit = "spp.farmer"

    farmer_marital_status = fields.Selection(
        selection_add=[
            ("married_monogamous", "Married Monogamous"),
            ("married_polygamous", "Married Polygamous"),
        ]
    )
    farmer_highest_education_level = fields.Selection(
        selection_add=[
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("certificate", "Certificate"),
            ("diploma", "Diploma"),
            ("university", "University"),
            ("tertiary", "Tertiary"),
        ],
    )
