from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestChangeRequestEditFarmer(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create required test data
        self.group = self.env["res.partner"].create(
            {
                "name": "Test Group",
                "is_registrant": True,
                "is_group": True,
            }
        )

        self.farmer = self.env["res.partner"].create(
            {
                "name": "Test Farmer",
                "is_registrant": True,
                "is_group": False,
            }
        )

        # Create a change request
        self.change_request = self.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.edit.farmer",
                "registrant_id": self.group.id,
            }
        )

        # Create the edit farmer request
        self.edit_farmer_request = self.env["spp.change.request.edit.farmer"].create(
            {
                "change_request_id": self.change_request.id,
                "registrant_id": self.group.id,
                "farmer_id": self.farmer.id,
            }
        )

    def test_birthdate_validation(self):
        """Test that birthdate cannot be in the future"""
        future_date = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.edit_farmer_request.birthdate = future_date
            self.edit_farmer_request._onchange_birthdate()

    def test_validate_data(self):
        """Test data validation"""
        # Test without farmer_id
        self.edit_farmer_request.farmer_id = False
        with self.assertRaises(ValidationError):
            self.edit_farmer_request.validate_data()

        # Test with farmer_id
        self.edit_farmer_request.farmer_id = self.farmer.id
        self.edit_farmer_request.validate_data()  # Should not raise error

    def test_update_live_data(self):
        """Test updating farmer data"""
        # Set new values
        self.edit_farmer_request.write(
            {
                "family_name": "New Family Name",
                "given_name": "New Given Name",
                "mobile_tel": "+1234567890",
                "farmer_national_id": "ID123456",
                "email": "test@example.com",
            }
        )

        # Update live data
        updated_farmer = self.edit_farmer_request.update_live_data()

        # Verify updates
        self.assertEqual(updated_farmer.family_name, "New Family Name")
        self.assertEqual(updated_farmer.given_name, "New Given Name")
        self.assertEqual(updated_farmer.email, "test@example.com")

        # Verify phone number
        phone = self.env["g2p.phone.number"].search([("partner_id", "=", updated_farmer.id)])
        self.assertEqual(phone.phone_no, "+1234567890")

        # Verify national ID
        reg_id = self.env["g2p.reg.id"].search(
            [
                ("partner_id", "=", updated_farmer.id),
                ("id_type", "=", self.env.ref("spp_farmer_registry_base.id_type_national_id").id),
            ]
        )
        self.assertEqual(reg_id.value, "ID123456")
