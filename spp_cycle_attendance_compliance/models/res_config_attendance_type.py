from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SPPResConfigAttendanceType(models.Model):
    _name = "spp.res.config.attendance.type"
    _description = "Config Attendance Type"
    _order = "name ASC"

    name = fields.Char(required=True)
    description = fields.Char()
    external_id = fields.Integer(required=True)
    external_source = fields.Char(required=True)
    set_as_default = fields.Boolean()

    _sql_constraints = [
        (
            "name",
            "unique (name)",
            "Name must be unique.",
        ),
    ]

    @api.constrains("set_as_default")
    def _check_only_one_default(self):
        if self.set_as_default:
            default_records = self.search([("set_as_default", "=", True), ("id", "!=", self.id)])
            if default_records:
                raise ValidationError(
                    "Another record is already set as default. Only one record can be set as default at a time."
                )
