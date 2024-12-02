from odoo import fields, models


class SPPAttendanceLocation(models.Model):
    _name = "spp.attendance.location"
    _description = "Attendance Location"
    _order = "name ASC"

    name = fields.Char(required=True)
    description = fields.Char()
