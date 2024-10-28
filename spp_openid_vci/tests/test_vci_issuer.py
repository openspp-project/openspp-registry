from unittest.mock import Mock, patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from ..models.res_partner import SPPRegistry as ResPartner


class VCIIssuer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.res_partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.vci_issuer = cls.env["g2p.openid.vci.issuers"].create(
            {
                "name": "TestIssuer",
                "issuer_type": "Registry",
                "scope": "openid",
            }
        )

        cls.id_type = cls.env["g2p.id.type"].create({"name": "Test ID Type"})
        cls.encryption_provider_id = cls.env["g2p.encryption.provider"].create(
            {
                "name": "Test Provider",
                "type": "jwcrypto",
            }
        )
        cls.encryption_provider_id.generate_and_store_jwcrypto_key()

        cls.vci_issuer_complete = cls.env["g2p.openid.vci.issuers"].create(
            {
                "name": "TestIssuerComplete",
                "issuer_type": "Registry",
                "scope": "openid",
                "auth_sub_id_type_id": cls.id_type.id,
                "encryption_provider_id": cls.encryption_provider_id.id,
            }
        )
        cls.res_partner_complete = cls.env["res.partner"].create({"name": "Test Partner Complete"})
        cls.env["g2p.reg.id"].create(
            {
                "partner_id": cls.res_partner_complete.id,
                "id_type": cls.id_type.id,
                "value": "Test Value",
            }
        )

        cls.test_issue_vc_json = {
            "credential_configurations_supported": None,
            "credential_endpoint": "http://localhost:8080/api/v1/vci/credential",
            "credential_issuer": "http://localhost:8080",
            "credentials_supported": [
                {
                    "credential_definition": {
                        "credentialSubject": {
                            "UIN": {"display": [{"locale": "en", "name": "Beneficiary " "ID"}]},
                            "address": {"display": [{"locale": "en", "name": "Address"}]},
                            "dateOfBirth": {"display": [{"locale": "en", "name": "Date " "of " "Birth"}]},
                            "fullName": {"display": [{"locale": "en", "name": "Name"}]},
                            "gender": {"display": [{"locale": "en", "name": "Gender"}]},
                            "nationalID": {"display": [{"locale": "en", "name": "National " "ID"}]},
                        },
                        "type": ["VerifiableCredential", "Registry"],
                    },
                    "credential_signing_alg_values_supported": ["RS256"],
                    "cryptographic_binding_methods_supported": ["did:jwk"],
                    "display": [
                        {
                            "background_color": "#12107c",
                            "locale": "en",
                            "logo": {
                                "alt_text": "a square logo " "of a OpenG2P",
                                "url": "http://localhost:8080/g2p_openid_vci/static/description/icon.png",
                            },
                            "name": "OpenG2P Registry Credential",
                            "text_color": "#FFFFFF",
                        }
                    ],
                    "format": "ldp_vc",
                    "id": "Registry",
                    "order": ["fullName", "gender", "dateOfBirth"],
                    "proof_types_supported": ["jwt"],
                    "scope": "IndividualRegistry",
                }
            ],
        }

    def test_validate_vci_issuer(self):
        with self.assertRaisesRegex(UserError, "No issuer found."):
            self.res_partner._validate_vci_issuer(None)

        with self.assertRaisesRegex(UserError, "No auth sub id type found in the issuer."):
            self.res_partner._validate_vci_issuer(self.vci_issuer)

        self.vci_issuer.auth_sub_id_type_id = self.id_type

        with self.assertRaisesRegex(UserError, "No encryption provider found in the issuer."):
            self.res_partner._validate_vci_issuer(self.vci_issuer)

        self.vci_issuer.encryption_provider_id = self.encryption_provider_id

        self.res_partner._validate_vci_issuer(self.vci_issuer)

    @patch("requests.get")
    def test_issue_vc(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_issue_vc_json
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(
            UserError, f"No Registrant found with this ID Type: {self.vci_issuer.auth_sub_id_type_id.name}."
        ):
            self.res_partner._issue_vc(self.vci_issuer)

        with patch.object(type(self.vci_issuer), "issue_vc", return_value=None) as issue_vc:
            self.res_partner_complete._issue_vc(self.vci_issuer_complete)
            issue_vc.assert_called_once()

    def test_create_qr_code(self):
        qr_img = self.res_partner_complete._create_qr_code("Test Data")
        self.assertIsNotNone(qr_img)
        self.assertIsInstance(qr_img, bytes)

    def test_registry_issue_card(self):
        registry_issue_card_action = self.res_partner_complete.registry_issue_card()

        form_id = self.env.ref("spp_openid_vci.issue_card_wizard").id

        self.assertIsNotNone(registry_issue_card_action)
        self.assertIsInstance(registry_issue_card_action, dict)
        self.assertEqual(registry_issue_card_action.get("type"), "ir.actions.act_window")
        self.assertEqual(registry_issue_card_action.get("res_model"), "spp.issue.card.wizard")
        self.assertEqual(registry_issue_card_action.get("name"), "Issue Card")
        self.assertEqual(registry_issue_card_action.get("view_id"), form_id)
        self.assertEqual(registry_issue_card_action["context"]["default_partner_id"], self.res_partner_complete.id)

    @patch.object(ResPartner, "_validate_vci_issuer")
    @patch.object(ResPartner, "_issue_vc")
    def test_issue_vc_qr(self, mock_vci_issuer, mock_issue_vc):
        mock_vci_issuer.return_value = True
        mock_issue_vc.return_value = {}

        vc_qr = self.res_partner_complete._issue_vc_qr(self.vci_issuer_complete)

        self.assertIsNotNone(vc_qr)
        self.assertIsInstance(vc_qr, dict)
        self.assertEqual(vc_qr.get("type"), "ir.actions.report")

    def test_sign_and_issue_credential(self):
        credential_data = {
            "test_key": "test_value",
        }
        credential = self.vci_issuer_complete.sign_and_issue_credential(credential_data)

        self.assertIsNotNone(credential)
        self.assertIsInstance(credential, dict)
        self.assertIn("test_key", credential)
        self.assertIn("proof", credential)
        self.assertIn("jws", credential["proof"])
        self.assertIn("type", credential["proof"])
        self.assertIn("verificationMethod", credential["proof"])
        self.assertIn("proofPurpose", credential["proof"])
        self.assertIn("created", credential["proof"])
        self.assertIn("@context", credential["proof"])
