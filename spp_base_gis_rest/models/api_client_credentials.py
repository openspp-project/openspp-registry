import calendar
import os
import uuid
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.spp_oauth.tools import calculate_signature

TOKEN_EXPIRATION_MIN = os.environ.get("SPP_BASE_GIS_TOKEN_EXP_MIN", 10)


class GisApiClientCredential(models.Model):
    _name = "spp.gis.api.client.credential"
    _description = "SPP GIS Client Credential"

    @api.model
    def _generate_client_id(self):
        client_id = str(uuid.uuid4())
        while self.search_count([("client_id", "=", client_id)]):
            client_id = str(uuid.uuid4())

        return client_id

    @api.model
    def _generate_client_secret(self):
        client_secret = str(uuid.uuid4())
        while self.search_count([("client_secret", "=", client_secret)]):
            client_secret = str(uuid.uuid4())

        return client_secret

    @api.model
    def _generate_client_token(self):
        client_token = str(uuid.uuid4())
        while self.search_count([("client_token", "=", client_token)]):
            client_token = str(uuid.uuid4())

        return client_token

    name = fields.Char("Client Name", required=True)
    auth_type = fields.Selection(
        [
            ("bearer", "Bearer"),
            ("basic", "Basic"),
        ],
        required=True,
        default="bearer",
    )

    # bearer fields
    client_id = fields.Char(required=True, readonly=True, default=_generate_client_id)
    client_secret = fields.Char(required=True, readonly=True, default=_generate_client_secret)

    # basic fields
    client_token = fields.Char(required=True, readonly=True, default=_generate_client_token)

    show_button_clicked = fields.Boolean("Viewed?")

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Client Name must be unique !"),
        ("client_id_uniq", "unique(client_id)", "Client ID must be unique !"),
        (
            "client_secret_uniq",
            "unique(client_secret)",
            "Client Secret must be unique !",
        ),
    ]

    ALLOW_EXPORT = False

    @api.model
    def generate_access_token(self):
        today = datetime.today()
        expiry_datetime = today + timedelta(minutes=TOKEN_EXPIRATION_MIN)

        header = {"alg": "RS256", "typ": "JWT"}
        payload = {
            "iat": calendar.timegm(today.timetuple()),
            "exp": calendar.timegm(expiry_datetime.timetuple()),
            "iss": "openspp:auth-service",
        }

        return calculate_signature(header, payload)

    def show_credentials(self):
        self.ensure_one()

        if not self.show_button_clicked:
            action = self.env[self._name].get_formview_action()
            form_id = self.env.ref("spp_base_gis_rest.spp_gis_api_client_credential_view_credentials").id

            action.update(
                {
                    "views": [(form_id, "form")],
                    "target": "new",
                    "type": "ir.actions.act_window",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_id": self.id,
                }
            )

            self.update(
                {
                    "show_button_clicked": True,
                }
            )
        else:
            raise UserError(_("Client ID and Client Secret is already showed once."))

        return action

    def export_data(self, fields_to_export):
        if not self.ALLOW_EXPORT:
            raise UserError(_("Not allowed to export on this model."))

        return super().export_data(fields_to_export)
