from odoo import fields, models


class OpenSPPEthnicGroup(models.Model):
    _name = "spp.ethnic.group"
    _description = "Ethnic Group"

    name = fields.Char("Ethnic Group", required=True)
    ethnic_group_id = fields.Char("Code", required=True)

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "Name must be unique!",
        ),
        (
            "ethnic_group_id_uniq",
            "unique(ethnic_group_id)",
            "Code must be unique!",
        ),
    ]
