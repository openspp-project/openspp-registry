from odoo import fields, models


class SPPResConfigAttendanceLocation(models.Model):
    _name = "spp.res.config.attendance.location"
    _description = "Config Attendance Location"
    _order = "name ASC"

    name = fields.Char(required=True)
    description = fields.Char()
    external_id = fields.Integer(required=True)
    external_source = fields.Char(required=True)

    _sql_constraints = [
        (
            "name",
            "unique (name)",
            "Name must be unique.",
        ),
    ]
