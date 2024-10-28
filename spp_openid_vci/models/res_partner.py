import base64
import calendar
import json
from datetime import datetime
from io import BytesIO

import qrcode
import requests
from qrcode.image.pil import PilImage

from odoo import _, fields, models
from odoo.exceptions import UserError


class SPPRegistry(models.Model):
    _inherit = "res.partner"

    vc_qr_code = fields.Binary(string="VC QR Code", attachment=True)

    def _validate_vci_issuer(self, vci_issuer):
        if not vci_issuer:
            raise UserError(_("No issuer found."))

        if not vci_issuer.auth_sub_id_type_id:
            raise UserError(_("No auth sub id type found in the issuer."))

        if not vci_issuer.encryption_provider_id:
            raise UserError(_("No encryption provider found in the issuer."))

    def _issue_vc(self, vci_issuer):
        self.ensure_one()

        encryption_provider_id = vci_issuer.encryption_provider_id

        reg_id = self.env["g2p.reg.id"].search(
            [("partner_id", "=", self.id), ("id_type", "=", vci_issuer.auth_sub_id_type_id.id)]
        )
        if not reg_id:
            raise UserError(f"No Registrant found with this ID Type: {vci_issuer.auth_sub_id_type_id.name}.")

        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url").rstrip("/")

        url = f"{web_base_url}/api/v1/vci/.well-known/openid-credential-issuer/{vci_issuer.name}"
        try:
            credential_issuer_response = requests.get(url, timeout=5)
        except requests.exceptions.Timeout as e:
            raise UserError(_("The request to the credential issuer timed out.")) from e
        issuer_data = credential_issuer_response.json()

        credential_issuer = f"{issuer_data['credential_issuer']}/api/v1/security"
        credentials_supported = issuer_data.get("credentials_supported", None)
        credential_request = credentials_supported[0]

        today = datetime.today()

        encryption_provider_id = vci_issuer.encryption_provider_id

        dict_data = {
            "sub": reg_id.value,
            "name": "OpenSPP",
            "iat": calendar.timegm(today.timetuple()),
            "scope": vci_issuer.scope,
            "iss": credential_issuer,
        }

        signed_data = encryption_provider_id.jwt_sign(data=dict_data)

        return self.env["g2p.openid.vci.issuers"].issue_vc(credential_request, signed_data)

    def _create_qr_code(self, data):
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            image_factory=PilImage,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image()

        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        temp.close()

        return qr_img

    def registry_issue_card(self):
        self.ensure_one()

        form_id = self.env.ref("spp_openid_vci.issue_card_wizard").id
        action = {
            "name": _("Issue Card"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.issue.card.wizard",
            "target": "new",
            "context": {
                "default_partner_id": self.id,
            },
        }
        return action

    def _issue_vc_qr(self, vci_issuer):
        self.ensure_one()

        self._validate_vci_issuer(vci_issuer)

        result = self._issue_vc(vci_issuer)

        qr_img = self._create_qr_code(json.dumps(result))

        self.vc_qr_code = qr_img

        admission_form = self.env.ref("spp_openid_vci.action_generate_id_card").report_action(self, config=False)
        return admission_form
