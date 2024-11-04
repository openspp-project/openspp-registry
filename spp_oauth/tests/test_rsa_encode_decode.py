from unittest.mock import patch

from odoo.tests.common import TransactionCase

from ..tools.rsa_encode_decode import calculate_signature, verify_and_decode_signature

MOCK_PRIVATE_KEY = "any_private_key"

MOCK_PUBLIC_KEY = "any_public_key"


class TestRSA(TransactionCase):
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.jwt.encode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_private_key")
    def test_calculate_signature(self, mock_get_private_key, mock_encode):
        mock_encode.return_value = "mocked_signature"
        mock_get_private_key.return_value = MOCK_PRIVATE_KEY

        header = {"typ": "JWT"}
        payload = {"data": "test"}
        signature = calculate_signature(header, payload)

        self.assertEqual(signature, "mocked_signature")

    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.jwt.decode")
    @patch("odoo.addons.spp_oauth.tools.rsa_encode_decode.get_public_key")
    def test_verify_and_decode_signature(self, mock_get_public_key, mock_decode):
        mock_decode.return_value = {"data": "test"}
        mock_get_public_key.return_value = MOCK_PUBLIC_KEY

        access_token = "mocked_access_token"

        decoded = verify_and_decode_signature(access_token)

        self.assertEqual(decoded, {"data": "test"})
