from unittest.mock import patch

from odoo.tests.common import TransactionCase


class ResPartnerTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._create_test_data()

    @classmethod
    def _create_test_data(cls):
        """Helper method to create areas and partners for the test."""
        cls.center_area_1 = cls.env["spp.area"].create({"draft_name": "Center Area 1"})
        cls.center_area_2 = cls.env["spp.area"].create({"draft_name": "Center Area 2"})
        cls.partner_1 = cls.env["res.partner"].create({"name": "Partner 1", "area_id": cls.center_area_1.id})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Partner 2", "area_id": cls.center_area_2.id})

    def _mock_center_area_ids(self):
        """Helper to mock the center_area_ids as a recordset."""
        mock_recordset = self.env["spp.area"].browse([self.center_area_1.id])
        return patch(
            "odoo.addons.spp_user_roles.models.user.ResUsersCustomSPP.center_area_ids",
            new_callable=lambda: mock_recordset,
        )

    def test_search_read(self):
        """Test the standard and mocked behavior of search_read."""
        partners = self.env["res.partner"]

        # Test the standard search_read behavior
        result = partners.search_read(domain=[], fields=["id", "name", "area_id"])
        self.assertEqual(len(result), partners.search_count([]))

        # Test search_read with mocked area
        with self._mock_center_area_ids():
            result = partners.search_read(domain=[], fields=["id", "name", "area_id"])
            self._check_partner_search_result(result, self.partner_1)

    def test_web_search_read(self):
        """Test the standard and mocked behavior of web_search_read."""
        partners = self.env["res.partner"]

        view = partners.get_view(view_id=None, view_type="form")
        spec = partners._get_fields_spec(view)

        # Test the standard web_search_read behavior
        result = partners.web_search_read(domain=[], specification=spec)
        self.assertEqual(len(result["records"]), partners.search_count([]))

        # Test web_search_read with mocked area
        with self._mock_center_area_ids():
            result = partners.web_search_read(domain=[], specification=spec)
            self.assertEqual(len(result["records"]), 1)
            self.assertEqual(result["records"][0]["id"], self.partner_1.id)

    def _check_partner_search_result(self, result, expected_partner):
        """Reusable assertion to validate the search result."""
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result,
            [
                {
                    "id": expected_partner.id,
                    "name": expected_partner.name,
                    "area_id": (expected_partner.area_id.id, expected_partner.area_id.draft_name),
                }
            ],
        )
