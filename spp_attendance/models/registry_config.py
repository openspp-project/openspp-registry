from odoo import _, api, fields, models


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    server_url = fields.Char(
        string="Server URL",
        config_parameter="spp_attendance.server_url",
        default=lambda self: self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
    )

    attendance_auth_endpoint = fields.Char(
        string="Auth Endpoint",
        config_parameter="spp_attendance.attendance_auth_endpoint",
        default="/oauth2/client/token",
    )
    access_token_mapping = fields.Char(
        string="Access Token Mapping",
        config_parameter="spp_attendance.access_token_mapping",
        default="access_token",
    )
    attendance_import_endpoint = fields.Char(
        string="Import Endpoint",
        config_parameter="spp_attendance.attendance_import_endpoint",
        default="/registry/sync/search",
    )

    personal_information_mapping = fields.Char(
        string="Personal Information",
        config_parameter="spp_attendance.personal_information_mapping",
        default="message.search_response.0.data.reg_records",
    )
    person_identifier_mapping = fields.Char(
        string="Person Identifier",
        config_parameter="spp_attendance.person_identifier_mapping",
        default="identifier.0.identifier",
    )
    family_name_mapping = fields.Char(
        string="Family Name",
        config_parameter="spp_attendance.family_name_mapping",
        default="familyName",
    )
    given_name_mapping = fields.Char(
        string="Given Name",
        config_parameter="spp_attendance.given_name_mapping",
        default="givenName",
    )
    email_mapping = fields.Char(
        string="Email",
        config_parameter="spp_attendance.email_mapping",
        default="email",
    )
    phone_mapping = fields.Char(
        string="Phone",
        config_parameter="spp_attendance.phone_mapping",
        default="phoneNumbers.0.phone",
    )
    gender_mapping = fields.Char(
        string="Gender",
        config_parameter="spp_attendance.gender_mapping",
        default="sex",
    )

    date_unique = fields.Boolean(
        string="Unique Date",
        config_parameter="spp_attendance.date_unique",
        default=False,
        inverse="_onchange_unique_fields",
    )
    time_unique = fields.Boolean(
        string="Unique Time",
        config_parameter="spp_attendance.time_unique",
        default=False,
        inverse="_onchange_unique_fields",
    )
    type_unique = fields.Boolean(
        string="Unique Type",
        config_parameter="spp_attendance.type_unique",
        default=False,
        inverse="_onchange_unique_fields",
    )
    location_unique = fields.Boolean(
        string="Unique Location",
        config_parameter="spp_attendance.location_unique",
        default=False,
    )

    def action_import(self):
        self.ensure_one()

        form_id = self.env.ref("spp_attendance.import_attendance_wizard").id
        action = {
            "name": _("Import Attendance"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.import.attendance.wizard",
            "target": "new",
        }
        return action

    @api.onchange("date_unique", "time_unique", "type_unique")
    def _onchange_unique_fields(self):
        if not self.date_unique:
            self.time_unique = False
            self.type_unique = False
            self.location_unique = False
        if not self.time_unique:
            self.type_unique = False
            self.location_unique = False
        if not self.type_unique:
            self.location_unique = False

    @api.model
    def set_server_url(self):
        if not self.env["ir.config_parameter"].sudo().get_param("spp_attendance.server_url"):
            web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            self.env["ir.config_parameter"].sudo().set_param("spp_attendance.server_url", web_base_url)
