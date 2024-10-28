from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger

EXCLUDED_CHARACTERS = ["0", "O", "1", "I"]


class TestRegistrant(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_household = self.env["res.partner"].create(
            {
                "name": "Test Household 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self._test_individuals = self.create_registrant({"name": "TEST, INDIVIDUAL, 1"}) | self.create_registrant(
            {"name": "TEST, INDIVIDUAL, 2"}
        )
        self._partner = self.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )

    def create_registrant(self, vals):
        self.assertTrue(isinstance(vals, dict), "Return vals should be a dict!")
        vals.update(
            {
                "is_group": False,
                "is_registrant": True,
            }
        )
        model = self.env["res.partner"]
        # Since we gonna create res_partner records without required field `name`, which violate
        # database constraint for this table.
        # This is how we ensure everything won't be error:
        # 1. Using new() function to create virtual record
        # 2. Using virtual record to compute field value [just like Odoo frontend - backend operation]
        # 3. Convert virtual record to param and create real record inside Database by create()
        # See: https://github.com/odoo/odoo/blob/15.0/addons/stock/tests/common2.py#L13
        virtual_rec = model.new(vals)
        if "name" not in vals:
            virtual_rec._compute_name()
        return model.create(virtual_rec._convert_to_write(virtual_rec._cache))

    def test_01_compute_spp_id_normal_partner(self):
        self.assertFalse(
            bool(self._partner.spp_id),
            "Normal Odoo contact should not have spp_id",
        )

    def test_02_compute_spp_id_household(self):
        self.assertRegex(
            self._test_household.spp_id,
            r"^GRP_[a-zA-Z0-9]{8}$",
            "Household should have unique registrant id start with " "`GRP_` and following by 8 characters.",
        )
        for char in EXCLUDED_CHARACTERS:
            self.assertNotIn(
                char,
                self._test_household.spp_id.split("_")[-1],
                "Excluded characters should not be exist in unique spp_id",
            )

    def test_03_compute_spp_id_individual(self):
        for individual in self._test_individuals:
            self.assertRegex(
                individual.spp_id,
                r"^IND_[a-zA-Z0-9]{8}$",
                "Individual should have unique registrant id start with " "`IND_` and following by 8 characters.",
            )
            for char in EXCLUDED_CHARACTERS:
                self.assertNotIn(
                    char,
                    individual.spp_id.split("_")[-1],
                    "Excluded characters should not be exist in unique spp_id",
                )

    @mute_logger("odoo.sql_db")
    def test_04_compute_spp_id_unique_violation(self):
        with self.assertRaises(UniqueViolation):
            self._test_individuals[0].write(
                {
                    "spp_id": self._test_individuals[1].spp_id,
                }
            )

    @mute_logger("py.warnings")
    def test_05_check_spp_id(self):
        with self.assertRaisesRegex(ValidationError, "^.*not following correct format.{1}$"):
            # 7 characters spp_id
            self._test_household.write({"spp_id": "GRP_AAAAAA2"})
        with self.assertRaisesRegex(ValidationError, "^.*not following correct format.{1}$"):
            # '1' in spp_id
            self._test_individuals[0].write({"spp_id": "IND_AAAAAA21"})
        with self.assertRaisesRegex(ValidationError, "^.*not following correct format.{1}$"):
            # individual with spp_id starts with GRP_
            self._test_individuals[0].write({"spp_id": "GRP_AAAAAA22"})
        with self.assertRaisesRegex(ValidationError, "^.*not following correct format.{1}$"):
            # group with spp_id starts with IND_
            self._test_household.write({"spp_id": "IND_AAAAAA22"})
        self._partner.write({"spp_id": "IND_AAAAAA21"})

    def test_06__inverse_name(self):
        registrant_1 = self._test_individuals[0]
        registrant_2 = self._test_individuals[1]
        self.assertListEqual(
            [registrant_2.given_name, registrant_2.family_name, registrant_2.addl_name],
            ["INDIVIDUAL", "TEST", "2"],
            "Set name should set everything correctly with individual!",
        )
        self.assertListEqual(
            [registrant_1.given_name, registrant_1.family_name, registrant_1.addl_name],
            ["INDIVIDUAL", "TEST", "1"],
            "Set name should set everything correctly with individual!",
        )
        test_registrant = self.create_registrant({"name": "NGUYEN, NHAT"})
        self.assertListEqual(
            [
                test_registrant.given_name,
                test_registrant.family_name,
                test_registrant.addl_name,
            ],
            ["NHAT", "NGUYEN", False],
            "Set name should set everything correctly with individual!",
        )
        test_registrant = self.create_registrant({"name": "NHAT"})
        self.assertListEqual(
            [
                test_registrant.given_name,
                test_registrant.family_name,
                test_registrant.addl_name,
            ],
            ["NHAT", False, False],
            "Set name should set everything correctly with individual!",
        )

    def test_07__compute_name(self):
        test_registrant = self.create_registrant(
            {
                "given_name": "Nhat",
                "family_name": "Nguyen",
                "addl_name": "Minh",
            }
        )
        self.assertEqual(
            test_registrant.name,
            "NGUYEN, NHAT, MINH",
            "Compute name should compute for individual!",
        )
        test_group = self.env["res.partner"].create(
            {
                "name": "NGUYEN FAMILY",
                "family_name": "Nguyen",
                "is_registrant": True,
                "is_group": True,
            }
        )
        test_group._compute_name()
        self.assertEqual(
            test_group.name,
            "NGUYEN FAMILY",
            "Compute name should only compute for individual!",
        )

    def test_08_get_import_templates(self):
        import_template = self.env["res.partner"].get_import_templates()
        self.assertEqual(
            import_template,
            [{"label": "Import Template for Customers", "template": "/base/static/xls/res_partner.xlsx"}],
        )

        import_template = self.env["res.partner"].with_context(default_is_registrant=True).get_import_templates()
        self.assertEqual(
            import_template,
            [
                {
                    "label": "Import Template for Individuals",
                    "template": "/spp_registrant_import/static/xls/individual_registry.xlsx",
                }
            ],
        )

        import_template = (
            self.env["res.partner"]
            .with_context(default_is_registrant=True, default_is_group=True)
            .get_import_templates()
        )
        self.assertEqual(
            import_template,
            [
                {
                    "label": "Import Template for Groups",
                    "template": "/spp_registrant_import/static/xls/group_registry.xlsx",
                }
            ],
        )
