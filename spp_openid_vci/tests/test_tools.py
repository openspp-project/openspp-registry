from qrcode.image.pil import PilImage

from odoo.tests.common import TransactionCase

from ..tools import create_qr_code, delete_keys_except, qr_image


class VCITools(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_delete_keys_except(self):
        sample_data = {
            "name": "John Doe",
            "age": 30,
        }
        delete_keys_except(sample_data, "name")

        self.assertEqual(sample_data, {"name": "John Doe"})

        sample_data = {
            "name": "John Doe",
            "age": 30,
        }
        delete_keys_except(sample_data, ["age"])

        self.assertEqual(sample_data, {"age": 30})

    def test_qr_image(self):
        img = qr_image("Hello, World!")
        self.assertTrue(img)
        self.assertIsInstance(img, PilImage)

    def test_create_qr_code(self):
        img = create_qr_code("Hello, World!")
        self.assertTrue(img)
        self.assertIsInstance(img, bytes)
