from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSPPFarmSeason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test users
        cls.farm_user = cls.env["res.users"].create(
            {
                "name": "Farm User",
                "login": "farm_user",
                "groups_id": [(4, cls.env.ref("spp_farmer_registry_base.group_spp_farm_user").id)],
            }
        )

        cls.farm_manager = cls.env["res.users"].create(
            {
                "name": "Farm Manager",
                "login": "farm_manager",
                "groups_id": [(4, cls.env.ref("spp_farmer_registry_base.group_spp_farm_manager").id)],
            }
        )

        # Create test data
        cls.today = date.today()
        cls.season_vals = {
            "name": "Test Season 2024",
            "date_start": cls.today,
            "date_end": cls.today + timedelta(days=90),
            "description": "Test Season Description",
        }

    def test_01_season_creation(self):
        """Test season creation with different user roles"""
        # Test creation as user (should fail)
        with self.assertRaises(ValidationError):
            self.env["spp.farm.season"].with_user(self.farm_user).create(self.season_vals)

        # Test creation as manager (should succeed)
        season = self.env["spp.farm.season"].with_user(self.farm_manager).create(self.season_vals)
        self.assertEqual(season.state, "draft")
        self.assertTrue(season.can_activate)

    def test_02_state_transitions(self):
        """Test season state workflow"""
        vals = dict(self.season_vals, allow_overlap=True)
        season = self.env["spp.farm.season"].with_user(self.farm_manager).create(vals)

        # Test draft to active
        season.action_activate()
        self.assertEqual(season.state, "active")

        # Test active to closed
        season.action_close()
        self.assertEqual(season.state, "closed")

        # Test cannot reopen closed season
        with self.assertRaises(ValidationError):
            season.action_draft()

    def test_03_activity_integration(self):
        """Test season integration with activities"""
        vals = dict(self.season_vals, allow_overlap=True)
        season = self.env["spp.farm.season"].with_user(self.farm_manager).create(vals)
        season.action_activate()

        # Create activity
        activity = self.env["spp.farm.activity"].create(
            {
                "season_id": season.id,
                "activity_type": "crop",
                "purpose": "subsistence",
            }
        )

        # Test activity count
        self.assertEqual(season.activity_count, 1)

        # Test cannot close season with activities
        season.action_close()

        # Test cannot modify activity in closed season
        with self.assertRaises(ValidationError):
            activity.write({"purpose": "commercial"})

    def test_04_access_rights(self):
        """Test access control and permissions"""
        season = self.env["spp.farm.season"].with_user(self.farm_manager).create(self.season_vals)

        # Test user read access
        season.with_user(self.farm_user).read(["name", "state"])

        # Test user write access (should fail)
        with self.assertRaises(ValidationError):
            season.with_user(self.farm_user).write({"name": "New Name"})

        # Test manager full access
        season.with_user(self.farm_manager).write({"name": "Updated Name"})
        self.assertEqual(season.name, "Updated Name")

    def test_05_season_copy(self):
        """Test season duplication"""
        vals = dict(self.season_vals, allow_overlap=True)
        season = self.env["spp.farm.season"].with_user(self.farm_manager).create(vals)
        season.action_activate()

        # Create activity
        self.env["spp.farm.activity"].create(
            {
                "season_id": season.id,
                "activity_type": "crop",
                "purpose": "subsistence",
            }
        )

        # Copy season
        new_season = season.copy()
        self.assertEqual(new_season.state, "draft")
        self.assertEqual(len(new_season.activity_ids), 0)
        self.assertIn("(Copy)", new_season.name)

    def test_06_current_season(self):
        """Test current season detection"""
        # Create past season
        past_vals = dict(
            self.season_vals,
            name="Past Season",
            date_start=self.today - timedelta(days=180),
            date_end=self.today - timedelta(days=90),
            allow_overlap=True,
        )
        past_season = self.env["spp.farm.season"].with_user(self.farm_manager).create(past_vals)
        past_season.action_activate()

        # Create current season
        vals = dict(self.season_vals, allow_overlap=True)
        current_season = self.env["spp.farm.season"].with_user(self.farm_manager).create(vals)
        current_season.action_activate()

        # Test current season detection
        found_season = self.env["spp.farm.season"]._get_current_season()
        self.assertEqual(found_season, current_season)

    def test_07_concurrent_seasons(self):
        """Test concurrent season management"""
        # Create overlapping seasons with allow_overlap
        season1 = (
            self.env["spp.farm.season"]
            .with_user(self.farm_manager)
            .create(
                {
                    "name": "Main Season",
                    "date_start": self.today,
                    "date_end": self.today + timedelta(days=90),
                    "allow_overlap": True,
                }
            )
        )
        season1.action_activate()

        season2 = (
            self.env["spp.farm.season"]
            .with_user(self.farm_manager)
            .create(
                {
                    "name": "Sub Season",
                    "date_start": self.today + timedelta(days=30),
                    "date_end": self.today + timedelta(days=60),
                    "allow_overlap": True,
                }
            )
        )
        season2.action_activate()

        # Verify both seasons are active
        active_seasons = self.env["spp.farm.season"].search(
            [
                ("state", "=", "active"),
                ("date_start", "<=", self.today + timedelta(days=45)),
                ("date_end", ">=", self.today + timedelta(days=45)),
            ]
        )
        self.assertEqual(len(active_seasons), 2)
