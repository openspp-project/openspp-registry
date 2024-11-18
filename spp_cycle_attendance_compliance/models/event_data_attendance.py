from odoo import fields, models


class SPPEventDataAttendance(models.Model):
    _name = "spp.event.attendance"
    _description = "Event Data for Attendance"

    individual_id = fields.Many2one("res.partner", string="Individual", readonly=True)
    attendance_date = fields.Date(required=True, default=fields.Date.today(), string="Date", readonly=True)
    attendance_time = fields.Char(required=True, string="Time", default="00:00:00", readonly=True)
    attendance_type_id = fields.Many2one("spp.res.config.attendance.type", string="Type", readonly=True)
    attendance_location_id = fields.Many2one("spp.res.config.attendance.location", string="Location", readonly=True)
    attendance_description = fields.Text(Char="Description", readonly=True)
    attendance_external_url = fields.Char(string="External URL", readonly=True)
    submitted_by = fields.Char(required=True, readonly=True)
    submitted_datetime = fields.Char(
        required=True, default=lambda self: fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S"), readonly=True
    )
    submission_source = fields.Char(readonly=True)

    event_data_source = fields.Char(readonly=True)
    event_data_external_id = fields.Integer(readonly=True)

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
