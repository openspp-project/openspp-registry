from odoo.tests.common import TransactionCase


class TestEligibilityManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.individual_id = cls.env["res.partner"].create(
            {
                "family_name": "Butay",
                "given_name": "Red",
                "name": "Red Butay",
                "is_group": False,
                "is_registrant": True,
            }
        )
        cls.group_id = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
                "is_registrant": True,
            }
        )

        cls.program = cls.env["g2p.program"].create({"name": "Test Program"})

        cls.manager_default = cls.env["g2p.program_membership.manager.default"].create(
            {
                "name": "Default",
                "program_id": cls.program.id,
            }
        )

    def test_prepare_exclusion_eligible_domain(self):
        domain = self.manager_default._prepare_exclusion_eligible_domain()
        self.assertIsInstance(domain, list)
        self.assertEqual(len(domain), 2)
        self.assertIn(("disabled", "=", False), domain)
        self.assertIn(("is_group", "=", True), domain)

        self.program.target_type = "individual"
        domain = self.manager_default._prepare_exclusion_eligible_domain()
        self.assertIsInstance(domain, list)
        self.assertEqual(len(domain), 2)
        self.assertIn(("disabled", "=", False), domain)
        self.assertIn(("is_group", "=", False), domain)

    def test_import_eligible_registrants(self):
        count = self.manager_default.import_eligible_registrants()
        self.assertEqual(count, 1)

        self.manager_default.enable_exclusion_filter = True
        count = self.manager_default.import_eligible_registrants()
        self.assertEqual(count, 0)
