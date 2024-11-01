import json

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.model
    def _get_default_attendance_server_url(self):
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return web_base_url

    attendance_server_url = fields.Char(
        string="Server URL",
        config_parameter="spp_cycle_attendance_compliance.attendance_server_url",
        default=_get_default_attendance_server_url,
    )
    attendance_auth_endpoint = fields.Char(
        string="Auth Endpoint",
        config_parameter="spp_cycle_attendance_compliance.attendance_auth_endpoint",
        default="/auth/token",
    )
    attendance_client_id = fields.Char(
        string="Client ID",
        config_parameter="spp_cycle_attendance_compliance.attendance_client_id",
    )
    attendance_client_secret = fields.Char(
        string="Client Secret",
        config_parameter="spp_cycle_attendance_compliance.attendance_client_secret",
    )
    attendance_compliance_endpoint = fields.Char(
        string="Compliance Endpoint",
        config_parameter="spp_cycle_attendance_compliance.attendance_compliance_endpoint",
        default="/attendances",
    )
    attendance_type_endpoint = fields.Char(
        string="Attendance Type Endpoint",
        config_parameter="spp_cycle_attendance_compliance.attendance_type_endpoint",
        default="/attendance/types",
    )
    attendance_location_endpoint = fields.Char(
        string="Attendance Location Endpoint",
        config_parameter="spp_cycle_attendance_compliance.attendance_location_endpoint",
        default="/attendance/locations",
    )

    def test_connection(self):
        self.ensure_one()
        auth_url = f"{self.attendance_server_url}{self.attendance_auth_endpoint}"
        client_id = self.attendance_client_id
        client_secret = self.attendance_client_secret
        data = json.dumps({"client_id": client_id, "client_secret": client_secret})
        response = requests.post(auth_url, data=data)

        if not response.status_code == 200:
            raise UserError("Connection Failed to Attendance Server. Reason: %s" % response.text)

        access_token = response.json().get("access_token")

        header = {"Authorization": f"Bearer {access_token}"}

        attendance_type_url = f"{self.attendance_server_url}{self.attendance_type_endpoint}"
        response = requests.get(attendance_type_url, headers=header)

        if not response.status_code == 200:
            raise UserError("Connection Failed to Attendance Type Endpoint. Reason: %s" % response.text)

        records = response.json().get("records", [])
        for record in records:
            attendance_type = self.env["spp.res.config.attendance.type"].search([("name", "=", record.get("name"))])
            if not attendance_type:
                self.env["spp.res.config.attendance.type"].create(
                    {
                        "name": record.get("name"),
                        "description": record.get("description"),
                        "external_id": record.get("id"),
                        "external_source": self.attendance_server_url,
                    }
                )
            else:
                attendance_type.write(
                    {
                        "name": record.get("name"),
                        "description": record.get("description"),
                        "external_id": record.get("id"),
                        "external_source": self.attendance_server_url,
                    }
                )

        attendance_location_url = f"{self.attendance_server_url}{self.attendance_location_endpoint}"

        response = requests.get(attendance_location_url, headers=header)
        if not response.status_code == 200:
            raise UserError("Connection Failed to Attendance Location Endpoint. Reason: %s" % response.text)

        records = response.json().get("records", [])
        for record in records:
            attendance_location = self.env["spp.res.config.attendance.location"].search(
                [("name", "=", record.get("name"))]
            )
            if not attendance_location:
                self.env["spp.res.config.attendance.location"].create(
                    {
                        "name": record.get("name"),
                        "description": record.get("description"),
                        "external_id": record.get("id"),
                        "external_source": self.attendance_server_url,
                    }
                )
            else:
                attendance_location.write(
                    {
                        "name": record.get("name"),
                        "description": record.get("description"),
                        "external_id": record.get("id"),
                        "external_source": self.attendance_server_url,
                    }
                )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import"),
                "message": _("Successfully imported Attendance Types and Locations."),
                "sticky": False,
                "type": "success",
            },
        }
