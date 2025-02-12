from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestChangeRequestAddFarmer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test group/registrant
        cls.group = cls.env["res.partner"].create(
            {
                "name": "Test Group",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Create test individual
        cls.individual = cls.env["res.partner"].create(
            {
                "name": "Test Individual",
                "family_name": "Test",
                "given_name": "Individual",
                "is_registrant": True,
                "is_group": False,
            }
        )

        # Create test role
        cls.role = cls.env["g2p.group.membership.kind"].create({"name": "Farmer"})

        # Create base change request
        cls.change_request = cls.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.add.farmer",
            }
        )

        # Create add farmer change request
        cls.add_farmer_request = cls.env["spp.change.request.add.farmer"].create(
            {
                "change_request_id": cls.change_request.id,
                "registrant_id": cls.group.id,
            }
        )

    def test_selection_request_type_ref_id(self):
        """Test the request type selection includes 'Add Farmer'"""
        selection = self.env["spp.change.request"]._selection_request_type_ref_id()
        self.assertIn(("spp.change.request.add.farmer", "Add Farmer"), selection)

    def test_check_phone_exist(self):
        """Test phone validation"""
        # Should pass with phone
        self.change_request._check_phone_exist()

    def test_onchange_registrant_id(self):
        """Test registrant change clears group members"""
        # Create test group member
        member = self.env["spp.change.request.group.members"].create(
            {
                "group_add_farmer_id": self.add_farmer_request.id,
                "individual_id": self.individual.id,
                "kind_ids": [(4, self.role.id)],
                "start_date": date.today(),
            }
        )
        self.add_farmer_request.group_member_ids = member

        # Change registrant
        new_group = self.env["res.partner"].create(
            {
                "name": "New Group",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self.add_farmer_request.registrant_id = new_group
        self.add_farmer_request._onchange_registrant_id()

        # Check group members cleared
        self.assertFalse(self.add_farmer_request.group_member_ids)
        self.assertEqual(self.add_farmer_request.change_request_id.registrant_id.id, new_group.id)

    def test_validate_data(self):
        """Test data validation"""
        # Should fail without group members
        with self.assertRaises(ValidationError) as cm:
            self.add_farmer_request.validate_data()
        self.assertIn("Need to add at least one farmer!", str(cm.exception))

    def test_update_live_data(self):
        """Test updating live data"""
        # Add group member
        member = self.env["spp.change.request.group.members"].create(
            {
                "group_add_farmer_id": self.add_farmer_request.id,
                "individual_id": self.individual.id,
                "kind_ids": [(4, self.role.id)],
                "start_date": date.today(),
            }
        )
        self.add_farmer_request.group_member_ids = member

        # Update live data
        self.add_farmer_request.update_live_data()

        # Check membership created
        membership = self.env["g2p.group.membership"].search(
            [("group", "=", self.group.id), ("individual", "=", self.individual.id)]
        )
        self.assertTrue(membership)
        self.assertEqual(membership.kind.ids, self.role.ids)
        self.assertEqual(membership.start_date.date(), date.today())

    def test_open_registrant_details_form(self):
        """Test opening registrant details form"""
        action = self.add_farmer_request.open_registrant_details_form()

        self.assertEqual(action["res_id"], self.group.id)
        self.assertEqual(action["target"], "new")
        self.assertFalse(action["context"]["create"])
        self.assertFalse(action["context"]["edit"])
        self.assertEqual(action["context"]["hide_from_cr"], 1)
        self.assertEqual(action["flags"]["mode"], "readonly")
