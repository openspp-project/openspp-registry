from odoo import fields, models


class Attendance(models.Model):
    _name = "spp.attendance.list"
    _description = "Attendance List"

    subscriber_id = fields.Many2one("spp.attendance.subscriber", required=True, readonly=True)
    attendance_date = fields.Date(required=True, default=lambda self: fields.Date.today(), string="Date")
    attendance_time = fields.Char(required=True, string="Time", default="00:00:00")

    attendance_type_id = fields.Many2one("spp.attendance.type", string="Type")
    attendance_location_id = fields.Many2one("spp.attendance.location", string="Location")
    attendance_description = fields.Text(string="Description")
    attendance_external_url = fields.Char(string="External URL")

    submitted_by = fields.Char(required=True)
    submitted_datetime = fields.Char(
        required=True, default=lambda self: fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    submission_source = fields.Char()

    def get_unique_domain(self):
        self.ensure_one()
        date_unique = self.env["ir.config_parameter"].sudo().get_param("spp_attendance.date_unique")
        time_unique = self.env["ir.config_parameter"].sudo().get_param("spp_attendance.time_unique")
        type_unique = self.env["ir.config_parameter"].sudo().get_param("spp_attendance.type_unique")
        location_unique = self.env["ir.config_parameter"].sudo().get_param("spp_attendance.location_unique")

        domain = []
        if date_unique:
            domain.append(("attendance_date", "=", self.attendance_date))
        if time_unique:
            domain.append(("attendance_time", "=", self.attendance_time))
        if type_unique:
            domain.append(("attendance_type_id", "=", self.attendance_type_id.id))
        if location_unique:
            domain.append(("attendance_location_id", "=", self.attendance_location_id.id))
        return domain

    def check_uniqueness(self, domain=None):
        for rec in self:
            domain = rec.get_unique_domain()
            if domain:
                new_domain = domain + [("subscriber_id", "=", rec.subscriber_id.id)]
                count = self.search_count(new_domain)
                if count > 0:
                    return False
        return True
