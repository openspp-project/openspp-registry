from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestChangeRequestCreateGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Define constants for refs
        cls.GROUP_KIND_HOUSEHOLD = "g2p_registry_group.group_kind_household"
        cls.GROUP_MEMBERSHIP_KIND_HEAD = "g2p_registry_membership.group_membership_kind_head"

        # Create required records
        cls.gender_male = cls.env["gender.type"].create({"code": "M", "value": "male"})

        # Create base change request
        cls.change_request = cls.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.create.group",
            }
        )

        # Create test record
        cls.create_group = cls.env["spp.change.request.create.group"].create(
            {
                "change_request_id": cls.change_request.id,
                "group_name": "Test Group",
                "group_kind": cls.env.ref(cls.GROUP_KIND_HOUSEHOLD).id,
                "family_name": "Doe",
                "given_name": "John",
                "additional_name": "Smith",
                "mobile_tel": "+1234567890",
                "sex": cls.gender_male.id,
                "birth_place": "Test City",
                "birthdate": date.today() - timedelta(days=365 * 30),
                "email": "test@example.com",
                "uid_number": "123456789012",
                "membership_kind": cls.env.ref(cls.GROUP_MEMBERSHIP_KIND_HEAD).id,
            }
        )

    def test_compute_full_name(self):
        """Test full name computation"""
        self.assertEqual(self.create_group.full_name, "Doe, John Smith")

        # Test with partial names
        self.create_group.write(
            {
                "family_name": "Doe",
                "given_name": False,
                "additional_name": False,
            }
        )
        self.create_group._compute_full_name()
        self.assertEqual(self.create_group.full_name, "Doe,  ")

    def test_birthdate_validation(self):
        """Test birthdate validation"""
        with self.assertRaises(ValidationError):
            self.create_group.birthdate = date.today() + timedelta(days=1)
            self.create_group._onchange_birthdate()

    def test_uid_number_validation(self):
        """Test UID number validation"""
        # Test invalid length
        with self.assertRaises(ValidationError):
            self.create_group.uid_number = "123"  # Less than 12 digits

        # Test valid UID
        self.create_group.uid_number = "123456789012"  # This should not raise an error

    def test_validate_data(self):
        """Test data validation"""
        # Test missing required fields
        test_record = self.env["spp.change.request.create.group"].create(
            {
                "change_request_id": self.change_request.id,
            }
        )

        with self.assertRaises(ValidationError) as cm:
            test_record.validate_data()
        self.assertIn("Group Name is required", str(cm.exception))
        self.assertIn("Group Kind is required", str(cm.exception))

    def test_update_live_data(self):
        """Test creation of individual and group"""
        self.create_group.update_live_data()

        # Check if group was created
        group = self.env["res.partner"].search([("name", "=", "Test Group"), ("is_group", "=", True)])
        self.assertTrue(group)
        self.assertEqual(group.kind, self.env.ref(self.GROUP_KIND_HOUSEHOLD))

        # Check if individual was created
        individual = self.env["res.partner"].search([("name", "=", "Doe, John Smith"), ("is_group", "=", False)])
        self.assertTrue(individual)
        self.assertEqual(individual.family_name, "Doe")
        self.assertEqual(individual.given_name, "John")
        self.assertEqual(individual.addl_name, "Smith")
        self.assertEqual(individual.phone, "+1234567890")
        self.assertEqual(individual.gender.id, self.gender_male.id)

        # Check if membership was created
        membership = self.env["g2p.group.membership"].search(
            [("group", "=", group.id), ("individual", "=", individual.id)]
        )
        self.assertTrue(membership)
        self.assertEqual(membership.kind[0].id, self.env.ref(self.GROUP_MEMBERSHIP_KIND_HEAD).id)

    def test_open_registrant_details_form(self):
        """Test opening registrant details form"""
        # Create a test registrant
        registrant = self.env["res.partner"].create(
            {
                "name": "Test Registrant",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self.create_group.registrant_id = registrant

        action = self.create_group.open_registrant_details_form()
        self.assertEqual(action["res_id"], registrant.id)
        self.assertEqual(action["target"], "new")
        self.assertFalse(action["context"]["create"])
        self.assertFalse(action["context"]["edit"])
