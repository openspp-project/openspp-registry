from unittest.mock import patch

from odoo.tests import TransactionCase


class TestEligibilityManager(TransactionCase):
    def test_01_selection_manager_ref_id(self):
        selection = self.env["g2p.eligibility.manager"]._selection_manager_ref_id()

        self.assertIn(("g2p.program_membership.manager.tags", "Tag-based Eligibility"), selection)


class TestTagBasedEligibilityManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()

        cls.program_id = cls.env["g2p.program"].create(
            {
                "name": "Test Program",
                "target_type": "individual",
            }
        )

        cls.tags_id = cls.env["g2p.registrant.tags"].create(
            {
                "name": "Test Tags",
            }
        )

        cls.area_id = cls.env["spp.area"].create(
            {
                "code": "101-1",
                "kind": cls.env.ref("spp_area_base.admin_area_kind").id,
                "draft_name": "1",
            }
        )

        cls.tag_manager = cls.env["g2p.program_membership.manager.tags"].create(
            {
                "name": "Tags Manager",
                "program_id": cls.program_id.id,
                "tags_id": cls.tags_id.id,
                "area_id": cls.area_id.id,
            }
        )

    def test_01_compute_custom_domain(self):
        self.tag_manager._compute_custom_domain()

        expected_result = f'[["tags_ids", "=", {self.tags_id.id}], ["area_id", "=", {self.area_id.id}]]'

        self.assertEqual(self.tag_manager.custom_domain, expected_result)

    def test_02_prepare_eligible_domain(self):
        domain = self.tag_manager._prepare_eligible_domain()

        expected_result = [
            ("disabled", "=", False),
            ("is_group", "=", False),
            ("tags_ids", "=", self.tags_id.id),
            ("area_id", "=", self.area_id.id),
        ]

        self.assertEqual(domain, expected_result)

    def test_03_get_initial_domain(self):
        self.program_id.target_type = "individual"
        domain = self.tag_manager._get_initial_domain()
        expected_result = [("disabled", "=", False), ("is_group", "=", False)]
        self.assertEqual(domain, expected_result)

        self.program_id.target_type = "group"
        domain = self.tag_manager._get_initial_domain()
        expected_result2 = [("disabled", "=", False), ("is_group", "=", True)]
        self.assertEqual(domain, expected_result2)

    def test_04_get_beneficiaries_by_tags(self):
        domain = self.tag_manager._get_beneficiaries_by_tags()

        expected_result = [
            ("tags_ids", "=", self.tags_id.id),
            ("area_id", "=", self.area_id.id),
        ]

        self.assertEqual(domain, expected_result)

    def test_05_enroll_eligible_registrants(self):
        membership = self.tag_manager.enroll_eligible_registrants(program_memberships=None)

        self.assertFalse(membership.id)
        self.assertEqual(membership._name, "g2p.program_membership")

    def test_06_verify_cycle_eligibility(self):
        membership = self.tag_manager.verify_cycle_eligibility(cycle=None, membership=None)

        self.assertFalse(membership.id)
        self.assertEqual(membership._name, "g2p.cycle.membership")

    def test_07_verify_eligibility(self):
        beneficiaries = self.tag_manager._verify_eligibility(membership=None)
        self.assertEqual(beneficiaries, [])

    @patch("odoo.addons.spp_eligibility_tags.models.eligibility_manager.len")
    def test_08_import_eligible_registrants(self, mocker):
        mocker.__name__ = "len__mocker"
        mocker.return_value = 1
        self.tag_manager.import_eligible_registrants()

        mocker.return_value = 1001
        self.tag_manager.import_eligible_registrants()

    def test_09_mark_import_as_done(self):
        self.tag_manager.mark_import_as_done()

        self.assertFalse(self.program_id.locked)
        self.assertFalse(self.program_id.locked_reason)

    def test_10_import_registrants(self):
        self.tag_manager._import_registrants(new_beneficiaries=[], do_count=True)
