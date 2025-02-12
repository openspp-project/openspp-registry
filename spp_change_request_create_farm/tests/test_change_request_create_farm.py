from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestChangeRequestCreateFarm(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create required base data
        self.gender_male = self.env["gender.type"].create({"code": "M", "value": "male"})

        # Create a company with country for phone validation
        self.company = self.env["res.company"].create(
            {"name": "Test Company", "country_id": self.env.ref("base.us").id}
        )

        # Create farm group kind if not exists
        self.farm_kind = self.env.ref("spp_farmer_registry_base.kind_farm", raise_if_not_found=False)
        if not self.farm_kind:
            self.farm_kind = self.env["g2p.group.kind"].create({"name": "Farm", "code": "farm"})

        # Create base change request
        self.change_request = self.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.create.farm",
            }
        )

        # Create the main change request create farm record
        self.cr_create_farm = self.env["spp.change.request.create.farm"].create(
            {
                "change_request_id": self.change_request.id,
                "group_name": "Test Farm",
                "group_kind": self.farm_kind.id,
                "farmer_family_name": "Doe",
                "farmer_given_name": "John",
                "farmer_mobile_tel": "+1 234-567-8901",
                "farmer_sex": self.gender_male.id,
                "farmer_birthdate": "1990-01-01",
                "farmer_household_size": "4",
                "farmer_highest_education_level": "secondary",
                "farmer_marital_status": "married",
                "land_name": "North Field",
                "land_acreage": 100.0,
                "details_legal_status": "self",
            }
        )

    def test_selection_request_type_ref_id(self):
        """Test the selection of request type includes create farm"""
        selection = self.env["spp.change.request"]._selection_request_type_ref_id()
        self.assertIn(("spp.change.request.create.farm", "Create Farm"), selection)

    def test_validate_data_success(self):
        """Test validation passes with all required fields"""
        # Should not raise any exception
        self.cr_create_farm.validate_data()

    def test_validate_data_missing_required(self):
        """Test validation fails when required fields are missing"""
        self.cr_create_farm.group_name = False
        with self.assertRaises(ValidationError):
            self.cr_create_farm.validate_data()

    def test_birthdate_validation(self):
        """Test birthdate cannot be in the future"""
        future_date = date.today().replace(year=date.today().year + 1)
        with self.assertRaises(ValidationError):
            self.cr_create_farm.farmer_birthdate = future_date
            self.cr_create_farm._onchange_farmer_birthdate()

    def test_update_live_data(self):
        """Test creation of actual farm record"""
        # Create agricultural activities
        crop_activity = self.env["spp.farm.activity"].create(
            {
                "species_id": self.env["spp.farm.species"].create({"name": "Test Crop", "species_type": "crop"}).id,
                "activity_type": "crop",
                "crop_cr_farm_id": self.cr_create_farm.id,
            }
        )

        livestock_activity = self.env["spp.farm.activity"].create(
            {
                "species_id": self.env["spp.farm.species"]
                .create({"name": "Test Livestock", "species_type": "livestock"})
                .id,
                "activity_type": "livestock",
                "live_cr_farm_id": self.cr_create_farm.id,
            }
        )

        aquaculture_activity = self.env["spp.farm.activity"].create(
            {
                "species_id": self.env["spp.farm.species"]
                .create({"name": "Test Aquaculture", "species_type": "aquaculture"})
                .id,
                "activity_type": "aquaculture",
                "aqua_cr_farm_id": self.cr_create_farm.id,
            }
        )

        # Create farm assets
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_type": self.env["asset.type"].create({"name": "Building"}).id,
                "asset_cr_farm_id": self.cr_create_farm.id,
            }
        )

        farm_machinery = self.env["spp.farm.asset"].create(
            {
                "machinery_type": self.env["machinery.type"].create({"name": "Tractor"}).id,
                "quantity": 1,
                "machine_working_status": "working",
                "machinery_cr_farm_id": self.cr_create_farm.id,
            }
        )

        # Update live data and get created group
        group = self.cr_create_farm.update_live_data()

        # Verify group creation
        self.assertTrue(group)
        self.assertEqual(group.name, "Test Farm")
        self.assertTrue(group.is_registrant)
        self.assertTrue(group.is_group)
        self.assertEqual(group.farmer_family_name, "Doe")
        self.assertEqual(group.farmer_given_name, "John")

        # Verify activities are linked
        self.assertTrue(crop_activity.crop_farm_id.id == group.id)
        self.assertTrue(livestock_activity.live_farm_id.id == group.id)
        self.assertTrue(aquaculture_activity.aqua_farm_id.id == group.id)

        # Verify assets are linked
        self.assertTrue(farm_asset.asset_farm_id.id == group.id)
        self.assertTrue(farm_machinery.machinery_farm_id.id == group.id)

    def test_check_phone_exist(self):
        """Test phone existence check"""
        # Test with farm request type (should not raise error)
        self.change_request.applicant_phone = False
        self.change_request._check_phone_exist()

    def test_open_registrant_details_form(self):
        """Test opening registrant details form returns correct action"""
        # First create a registrant
        registrant = self.env["res.partner"].create(
            {
                "name": "Test Registrant",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Assign registrant to change request
        self.cr_create_farm.registrant_id = registrant.id

        # Get the action
        action = self.cr_create_farm.open_registrant_details_form()

        # Verify action contents
        self.assertEqual(action["res_id"], registrant.id)
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["name"], "Group Details")
        self.assertFalse(action["context"]["create"])
        self.assertFalse(action["context"]["edit"])
        self.assertEqual(action["context"]["hide_from_cr"], 1)
        self.assertEqual(action["flags"]["mode"], "readonly")
