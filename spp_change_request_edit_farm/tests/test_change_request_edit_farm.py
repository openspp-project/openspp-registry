from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestChangeRequestEditFarm(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test data
        self.group_kind = self.env.ref("spp_farmer_registry_base.kind_farm")

        # Create a test farm/group
        self.test_farm = self.env["res.partner"].create(
            {
                "name": "Test Farm",
                "is_registrant": True,
                "is_group": True,
                "kind": self.group_kind.id,
            }
        )

        # Create a change request
        self.change_request = self.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.edit.farm",
            }
        )

    def test_01_create_edit_farm_request(self):
        """Test creating an edit farm change request"""
        edit_farm = self.env["spp.change.request.edit.farm"].create(
            {
                "change_request_id": self.change_request.id,
                "registrant_id": self.test_farm.id,
                "group_name": "Updated Farm Name",
                "land_name": "Test Parcel",
                "land_acreage": 100.0,
                "details_legal_status": "self",
            }
        )

        self.assertEqual(edit_farm.group_name, "Updated Farm Name")
        self.assertEqual(edit_farm.registrant_id, self.test_farm)

    def test_02_validate_data_no_registrant(self):
        """Test validation fails when no registrant is provided"""
        edit_farm = self.env["spp.change.request.edit.farm"].create(
            {
                "change_request_id": self.change_request.id,
                "group_name": "Test Farm",
            }
        )

        with self.assertRaises(ValidationError):
            edit_farm.validate_data()

    def test_03_update_live_data(self):
        """Test updating live data updates the farm record"""
        edit_farm = self.env["spp.change.request.edit.farm"].create(
            {
                "change_request_id": self.change_request.id,
                "registrant_id": self.test_farm.id,
                "group_name": "Updated Farm Name",
                "land_name": "New Parcel",
                "land_acreage": 150.0,
                "details_legal_status": "family",
            }
        )

        # Update live data
        updated_farm = edit_farm.update_live_data()

        # Check if farm was updated correctly
        self.assertEqual(updated_farm.name, "Updated Farm Name")
        self.assertEqual(updated_farm.land_name, "New Parcel")
        self.assertEqual(updated_farm.land_acreage, 150.0)
        self.assertEqual(updated_farm.details_legal_status, "family")

    def test_04_agricultural_activities(self):
        """Test adding agricultural activities to the change request"""
        edit_farm = self.env["spp.change.request.edit.farm"].create(
            {
                "change_request_id": self.change_request.id,
                "registrant_id": self.test_farm.id,
            }
        )

        # Create crop activity
        crop_activity = self.env["spp.farm.activity"].create(
            {
                "species_id": self.env["spp.farm.species"]
                .create(
                    {
                        "name": "Test Crop",
                        "species_type": "crop",
                    }
                )
                .id,
                "activity_type": "crop",
                "crop_cr_farm_id": edit_farm.id,
            }
        )

        # Create livestock activity
        livestock_activity = self.env["spp.farm.activity"].create(
            {
                "species_id": self.env["spp.farm.species"]
                .create(
                    {
                        "name": "Test Livestock",
                        "species_type": "livestock",
                    }
                )
                .id,
                "activity_type": "livestock",
                "live_cr_farm_id": edit_farm.id,
            }
        )

        # Create aquaculture activity
        aqua_activity = self.env["spp.farm.activity"].create(
            {
                "species_id": self.env["spp.farm.species"]
                .create(
                    {
                        "name": "Test Fish",
                        "species_type": "aquaculture",
                    }
                )
                .id,
                "activity_type": "aquaculture",
                "aqua_cr_farm_id": edit_farm.id,
            }
        )

        # Verify activities are linked to the change request
        self.assertTrue(crop_activity in edit_farm.farm_crop_act_ids)
        self.assertTrue(livestock_activity in edit_farm.farm_live_act_ids)
        self.assertTrue(aqua_activity in edit_farm.farm_aqua_act_ids)

        # Update live data and check if activities are linked to farm
        updated_farm = edit_farm.update_live_data()
        self.assertEqual(crop_activity.crop_farm_id, updated_farm)
        self.assertEqual(livestock_activity.live_farm_id, updated_farm)
        self.assertEqual(aqua_activity.aqua_farm_id, updated_farm)

    def test_05_farm_assets(self):
        """Test adding farm assets to the change request"""
        edit_farm = self.env["spp.change.request.edit.farm"].create(
            {
                "change_request_id": self.change_request.id,
                "registrant_id": self.test_farm.id,
            }
        )

        # Create farm asset
        asset = self.env["spp.farm.asset"].create(
            {
                "asset_type": self.env["asset.type"]
                .create(
                    {
                        "name": "Test Asset",
                    }
                )
                .id,
                "asset_cr_farm_id": edit_farm.id,
            }
        )

        # Create machinery asset
        machinery = self.env["spp.farm.asset"].create(
            {
                "machinery_type": self.env["machinery.type"]
                .create(
                    {
                        "name": "Tractor",
                    }
                )
                .id,
                "machinery_cr_farm_id": edit_farm.id,
                "quantity": 1,
                "machine_working_status": "working",
            }
        )

        self.assertTrue(asset in edit_farm.farm_asset_ids)
        self.assertTrue(machinery in edit_farm.farm_machinery_ids)

        # Update live data and check if assets are linked to farm
        updated_farm = edit_farm.update_live_data()
        self.assertEqual(asset.asset_farm_id, updated_farm)
        self.assertEqual(machinery.machinery_farm_id, updated_farm)
