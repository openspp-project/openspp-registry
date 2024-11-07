from odoo import api, fields, models


class AttendanceSubscriber(models.Model):
    _name = "spp.attendance.subscriber"
    _inherits = {
        "res.partner": "partner_id",
    }
    _description = "Attendance Subscriber"

    name = fields.Char(related="partner_id.name", inherited=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one("res.partner", readonly=True)
    attendance_list_ids = fields.One2many("spp.attendance.list", "subscriber_id")
    person_identifier = fields.Char(required=True, inverse="_inverse_person_identifier", store=True)

    partner_name = fields.Char(compute="_compute_partner_name", string="Complete Name")
    family_name = fields.Char(related="partner_id.family_name", inherited=True, required=True, readonly=False)
    given_name = fields.Char(related="partner_id.given_name", inherited=True, required=True, readonly=False)
    addl_name = fields.Char(related="partner_id.addl_name", inherited=True, readonly=False)
    email = fields.Char(
        related="partner_id.email", inherited=True, compute="_compute_partner", inverse="_inverse_partner", store=True
    )
    phone = fields.Char(
        related="partner_id.phone", inherited=True, compute="_compute_partner", inverse="_inverse_partner", store=True
    )
    mobile = fields.Char(
        related="partner_id.mobile", inherited=True, compute="_compute_partner", inverse="_inverse_partner", store=True
    )
    gender = fields.Char(related="partner_id.gender", inherited=True, readonly=False)

    _sql_constraints = [
        (
            "partner_id_uniq",
            "unique(partner_id)",
            "A subscriber with the same partner already exists.",
        ),
        (
            "person_identifier_uniq",
            "unique(person_identifier)",
            "A subscriber with the same person identifier already exists.",
        ),
    ]

    def _inverse_person_identifier(self):
        for record in self:
            record.partner_id.write({"identifier": record.person_identifier})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "partner_id" not in vals:
                partner_name = f"{vals.get('family_name')}, {vals.get('given_name')}"
                if vals.get("addl_name"):
                    partner_name += f" {vals.get('addl_name')}"
                if partner_id := self.env["res.partner"].search(
                    [
                        ("family_name", "=", vals.get("family_name")),
                        ("given_name", "=", vals.get("given_name")),
                        ("identifier", "=", vals.get("identifier")),
                    ],
                    limit=1,
                ):
                    vals["partner_id"] = partner_id.id
                else:
                    partner_id = self.env["res.partner"].create(
                        {
                            "name": partner_name,
                            "family_name": vals.get("family_name"),
                            "given_name": vals.get("given_name"),
                            "addl_name": vals.get("given_name"),
                            "email": vals.get("email"),
                            "phone": vals.get("phone"),
                            "mobile": vals.get("mobile"),
                            "identifier": vals.get("person_identifier"),
                            "gender": vals.get("gender"),
                        }
                    )
                    vals["partner_id"] = partner_id.id
        return super().create(vals_list)

    @api.depends("partner_id.name", "partner_id.email", "partner_id.phone", "partner_id.mobile")
    def _compute_partner(self):
        for record in self:
            if record.partner_id:
                record.write(
                    {
                        "email": record.partner_id.email,
                        "phone": record.partner_id.phone,
                        "mobile": record.partner_id.mobile,
                    }
                )

    def _inverse_partner(self):
        for record in self:
            if record.partner_id:
                record.partner_id.write(
                    {
                        "name": f"{record.family_name}, {record.given_name}",
                        "email": record.email,
                        "phone": record.phone,
                        "mobile": record.mobile,
                    }
                )

    @api.depends("family_name", "given_name")
    def _compute_partner_name(self):
        for record in self:
            if record.family_name and record.given_name:
                record.partner_name = f"{record.family_name}, {record.given_name}"
                if record.addl_name:
                    record.partner_name += f" {record.addl_name}"
            else:
                record.partner_name = ""

    def get_attendance_list(
        self,
        from_date=None,
        to_date=None,
        attendance_type_id=None,
        attendance_location_id=None,
        offset=0,
        limit=None,
    ):
        domain = [("subscriber_id", "=", self.id)]
        if from_date and to_date:
            domain += [("attendance_date", ">=", from_date), ("attendance_date", "<=", to_date)]
        if attendance_type_id:
            domain += [("attendance_type_id", "=", attendance_type_id)]
        if attendance_location_id:
            domain += [("attendance_location_id", "=", attendance_location_id)]

        attendance_list_ids = self.env["spp.attendance.list"].search(
            domain, offset=offset, limit=limit, order="attendance_date desc, attendance_time desc"
        )
        total_attendances = self.env["spp.attendance.list"].sudo().search_count(domain)
        number_of_days_present = list(
            set(self.env["spp.attendance.list"].sudo().search(domain).mapped("attendance_date"))
        )

        return total_attendances, {
            "person_id": self.person_identifier,
            "dates_present": number_of_days_present,
            "number_of_days_present": len(number_of_days_present),
            "attendance_list": [
                {
                    "id": attendance.id,
                    "date": attendance.attendance_date,
                    "time": attendance.attendance_time,
                    "attendance_type": {
                        "id": attendance.attendance_type_id.id,
                        "name": attendance.attendance_type_id.name,
                        "description": attendance.attendance_type_id.description,
                    }
                    if attendance.attendance_type_id
                    else {},
                    "attendance_location": {
                        "id": attendance.attendance_location_id.id,
                        "name": attendance.attendance_location_id.name,
                        "description": attendance.attendance_location_id.description,
                    }
                    if attendance.attendance_location_id
                    else {},
                    "attendance_description": attendance.attendance_description or "",
                    "attendance_external_url": attendance.attendance_external_url or "",
                    "submitted_by": attendance.submitted_by,
                    "submitted_datetime": attendance.submitted_datetime,
                    "submission_source": attendance.submission_source or "",
                }
                for attendance in attendance_list_ids
            ],
        }

    def get_attendance_info_list(self):
        attendance_infos = []
        for subscriber in self:
            attendance_infos.append(subscriber.get_attendance_subscriber_info())
        return attendance_infos

    def get_attendance_subscriber_info(self):
        self.ensure_one()
        return {
            "id": self.id,
            "person_id": self.person_identifier,
            "name": self.partner_name,
            "family_name": self.family_name,
            "given_name": self.given_name,
            "email": self.email,
            "phone": self.phone,
            "mobile": self.mobile,
        }
