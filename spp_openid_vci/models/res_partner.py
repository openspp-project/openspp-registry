import calendar
import json
import logging
from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..tools import create_qr_code

_logger = logging.getLogger(__name__)


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
            raise UserError(
                _("Registrant ({registry_name}) does not have ID with ID Type {id_type}.").format(
                    registry_name=self.name, id_type=vci_issuer.auth_sub_id_type_id.name
                )
            )

        issuer_data = self.env["g2p.openid.vci.issuers"].get_issuer_metadata_by_name(issuer_name=vci_issuer.name)

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

    def registry_issue_card(self):
        form_id = self.env.ref("spp_openid_vci.issue_card_wizard").id
        action = {
            "name": _("Issue Card"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.issue.card.wizard",
            "target": "new",
        }
        return action

    def _issue_vc_qr(self, vci_issuer):
        for rec in self:
            rec._validate_vci_issuer(vci_issuer)

            result = rec._issue_vc(vci_issuer)

            qr_img = create_qr_code(json.dumps(result))

            rec.vc_qr_code = qr_img

        admission_form = self.env.ref("spp_openid_vci.action_generate_id_card").report_action(self, config=False)

        return admission_form

    def _get_vc_issue_file_name(self):
        return "ID Card - %s" % self.name.replace("/", "").strip()
