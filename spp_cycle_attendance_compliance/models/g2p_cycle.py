import json
from urllib.parse import urlencode, urljoin

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import AND


class G2pCycle(models.Model):
    _inherit = "g2p.cycle"

    use_attendance_criteria = fields.Boolean(
        string="Use Attendance Compliance Criteria",
        help=_("If checked, attendance criteria will be used to filter beneficiaries."),
        default=True,
    )

    attendance_type_id = fields.Many2one(
        "spp.res.config.attendance.type",
        string="Attendance Type",
        help=_("Type of attendance to be taken for this program. Should be existing in the system of the API Server."),
    )
    attendance_location_id = fields.Many2one(
        "spp.res.config.attendance.location",
        string="Attendance Location",
        help=_(
            "Location of attendance to be taken for this program. Should be existing in the system of the API Server."
        ),
    )
    required_number_of_attendance = fields.Integer(
        string="Required Number of Attendance (Days)",
        default=10,
    )
    from_date = fields.Date()
    to_date = fields.Date()

    def _get_domain(self):
        domain = self._get_compliance_criteria_domain()
        if self.program_id.target_type == "individual":
            domain += AND([[("personal_identifier", "!=", False)]])
        return domain

    def default_url_params(self):
        params = {}
        if self.from_date:
            params["from_date"] = self.from_date
        if self.to_date:
            params["to_date"] = self.to_date
        if self.attendance_type_id:
            params["attendance_type"] = self.attendance_type_id.external_id
        if self.attendance_location_id:
            params["attendance_location"] = self.attendance_location_id.external_id
        return params

    def _check_and_retrieve_config_params(self, param, name):
        config_param = self.env["ir.config_parameter"].sudo().get_param(param)
        if not config_param:
            raise UserError(f"{name} is not configured.")
        return config_param

    def get_attendance_records(self, registrants):
        if not self.use_attendance_criteria:
            return

        attendance_server_url = self._check_and_retrieve_config_params(
            "spp_cycle_attendance_compliance.attendance_server_url", "Attendance Server URL"
        )
        auth_endpoint = self._check_and_retrieve_config_params(
            "spp_cycle_attendance_compliance.attendance_auth_endpoint", "Attendance Auth Endpoint"
        )

        attendance_auth_url = urljoin(attendance_server_url, auth_endpoint)

        attendance_client_id = self._check_and_retrieve_config_params(
            "spp_cycle_attendance_compliance.attendance_client_id", "Attendance Client ID"
        )
        attendance_client_secret = self._check_and_retrieve_config_params(
            "spp_cycle_attendance_compliance.attendance_client_secret", "Attendance Client Secret"
        )
        data = json.dumps({"client_id": attendance_client_id, "client_secret": attendance_client_secret})
        response = requests.post(attendance_auth_url, data=data)
        if response.status_code != 200:
            raise UserError(f"Connection to Attendance Server Failed. Reason: {response.text}")

        # access_token = response.json().get(access_token_mapping, None)
        access_token = response.json().get("access_token", None)
        if not access_token:
            raise UserError("Access Token not found in response.")

        attendance_compliance_endpoint = self._check_and_retrieve_config_params(
            "spp_cycle_attendance_compliance.attendance_compliance_endpoint", "Attendance Compliance Endpoint"
        )
        attendance_compliance_url = urljoin(attendance_server_url, attendance_compliance_endpoint)

        header = {"Authorization": f"Bearer {access_token}"}
        if self.program_id.target_type == "individual":
            data = json.dumps({"person_ids": registrants.mapped("personal_identifier")})
        else:
            data = json.dumps(
                {"person_ids": registrants.group_membership_ids.mapped("individual").mapped("personal_identifier")}
            )

        params = self.default_url_params()
        params["limit"] = max(len(registrants), 30)

        full_attendance_compliance_url = urljoin(attendance_compliance_url, "?" + urlencode(params))
        response = requests.get(full_attendance_compliance_url, headers=header, data=data)

        if response.status_code != 200:
            raise UserError(f"Connection to Attendance Compliance Server Failed. Reason: {response.text}")

        return response.json()

    def action_filter_beneficiaries_by_compliance_criteria(self):
        super().action_filter_beneficiaries_by_compliance_criteria()

        domain = self._get_domain()
        registrant_satisfied = self.env["res.partner"].sudo().search(domain)

        record_per_person = {}
        verified_person_id = []
        records = self.get_attendance_records(registrant_satisfied).get("records", [])
        for record in records:
            person_id = record.get("person_id", None)
            number_of_attendance = record.get("number_of_days_present", 0)
            record_per_person[person_id] = record
            if number_of_attendance >= self.required_number_of_attendance:
                verified_person_id.append(person_id)

        if self.program_id.target_type == "individual":
            self._create_attendance_event_data(registrant_satisfied, record_per_person)
            registrant_satisfied = registrant_satisfied.filtered(lambda r: r.personal_identifier in verified_person_id)
        else:
            compliant_members_ids = []
            for group in registrant_satisfied:
                members = group.group_membership_ids.mapped("individual")
                self._create_attendance_event_data(members, record_per_person)
                for member in members:
                    if member.personal_identifier in verified_person_id:
                        compliant_members_ids.append(group.id)
            compliant_members_ids = list(set(compliant_members_ids))
            registrant_satisfied = registrant_satisfied.filtered(lambda r: r.id in compliant_members_ids)

        membership_to_paused = self.cycle_membership_ids.filtered(lambda cm: cm.partner_id not in registrant_satisfied)
        membership_to_paused.state = "non_compliant"
        membership_to_enrolled = self.cycle_membership_ids - membership_to_paused
        membership_to_enrolled.state = "enrolled"

        if self.program_id.target_type == "group":
            for cycle_membership_id in self.cycle_membership_ids:
                for cycle_membership_attendance_id in cycle_membership_id.cycle_group_membership_attendance_ids:
                    individual_id = cycle_membership_attendance_id.individual_id
                    person_record = record_per_person.get(individual_id.personal_identifier, {})
                    person_number_of_days_present = person_record.get("number_of_days_present", 0)
                    cycle_membership_attendance_id.number_of_attendance_str = str(person_number_of_days_present)
                    if individual_id.personal_identifier in verified_person_id:
                        cycle_membership_attendance_id.state = "included"
                    else:
                        cycle_membership_attendance_id.state = "not_included"
        else:
            for cycle_membership_id in self.cycle_membership_ids:
                person_record = record_per_person.get(cycle_membership_id.partner_id.personal_identifier, {})
                person_number_of_days_present = person_record.get("number_of_days_present", 0)
                cycle_membership_id.number_of_attendance = person_number_of_days_present

        message = _("Successfully applied compliance criteria.")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Compliance Criteria"),
                "message": message,
                "sticky": False,
                "type": "success",
                "next": {
                    "type": "ir.actions.client",
                    "tag": "reload",
                },
            },
        }

    def _create_attendance_event_data(self, individual_ids, record_per_person):
        server_url = (
            self.env["ir.config_parameter"].sudo().get_param("spp_cycle_attendance_compliance.attendance_server_url")
        )
        attendance_type_mapping = {}
        attendance_type_ids = self.env["spp.res.config.attendance.type"].search([])
        for attendance_type in attendance_type_ids:
            attendance_type_mapping[
                f"{attendance_type.external_source}-{attendance_type.external_id}"
            ] = attendance_type.id

        attendance_location_mapping = {}
        attendance_location_ids = self.env["spp.res.config.attendance.location"].search([])
        for attendance_location in attendance_location_ids:
            attendance_location_mapping[
                f"{attendance_location.external_source}-{attendance_location.external_id}"
            ] = attendance_location.id

        for individual_id in individual_ids:
            record = record_per_person.get(individual_id.personal_identifier, {})
            if record:
                external_ids = []
                for attendance in record.get("attendance_list", []):
                    external_ids.append(attendance.get("id"))
                    attendance_type = attendance.get("attendance_type", {})
                    attendance_location = attendance.get("attendance_location", {})
                    event_attendance_vals = {
                        "individual_id": individual_id.id,
                        "attendance_date": attendance.get("date"),
                        "attendance_time": attendance.get("time"),
                        "attendance_type_id": attendance_type_mapping.get(
                            f"{server_url}-{attendance_type.get('id')}", False
                        ),
                        "attendance_location_id": attendance_location_mapping.get(
                            f"{server_url}-{attendance_location.get('id')}", False
                        ),
                        "attendance_description": attendance.get("attendance_description"),
                        "attendance_external_url": attendance.get("attendance_external_url"),
                        "submitted_by": attendance.get("submitted_by"),
                        "submitted_datetime": attendance.get("submitted_datetime"),
                        "submission_source": attendance.get("submission_source"),
                        "event_data_source": server_url,
                        "event_data_external_id": attendance.get("id"),
                    }
                    domain = [
                        ("individual_id", "=", individual_id.id),
                        ("event_data_source", "=", server_url),
                        ("event_data_external_id", "=", attendance.get("id")),
                    ]
                    event_attendance_id = self.env["spp.event.attendance"].search(domain, limit=1)
                    if not event_attendance_id:
                        new_event_attendance_id = self.env["spp.event.attendance"].create(event_attendance_vals)
                        self._create_event_data(individual_id, new_event_attendance_id)
                    else:
                        event_attendance_id.write(event_attendance_vals)

                # Delete all the attendance records that are not in the external_ids
                event_attendance_ids = self.env["spp.event.attendance"].search(
                    [
                        ("individual_id", "=", individual_id.id),
                        ("event_data_source", "=", server_url),
                        ("event_data_external_id", "not in", external_ids),
                    ]
                )
                if event_attendance_ids:
                    event_data_to_delete = self.env["spp.event.data"].search(
                        [("res_id", "in", event_attendance_ids.ids), ("model", "=", event_attendance_ids._name)]
                    )
                    event_attendance_ids.unlink()
                    event_data_to_delete.unlink()

    def _create_event_data(self, partner_id, res_id):
        return self.env["spp.event.data"].create(
            {
                "model": res_id._name,
                "partner_id": partner_id.id,
                "res_id": res_id.id,
            }
        )
