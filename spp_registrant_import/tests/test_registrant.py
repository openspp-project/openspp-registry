from psycopg2.errors import UniqueViolation

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
        self._test_individuals = self.env["res.partner"].create(
            [
                {
                    "name": "Test Individual 1",
                    "is_registrant": True,
                    "is_group": False,
                },
                {
                    "name": "Test Individual 2",
                    "is_registrant": True,
                    "is_group": False,
                },
            ]
        )
        self._partner = self.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )

    def test_01_compute_registrant_id_normal_partner(self):
        self.assertFalse(
            bool(self._partner.registrant_id),
            "Normal Odoo contact should not have registrant_id",
        )

    def test_02_compute_registrant_id_household(self):
        self.assertRegex(
            self._test_household.registrant_id,
            r"^GRP_[a-zA-Z0-9]{8}$",
            "Household should have unique registrant id start with "
            "`GRP_` and following by 8 characters.",
        )
        for char in EXCLUDED_CHARACTERS:
            self.assertNotIn(
                char,
                self._test_household.registrant_id.split("_")[-1],
                "Excluded characters should not be exist in unique registrant_id",
            )

    def test_03_compute_registrant_id_individual(self):
        for individual in self._test_individuals:
            self.assertRegex(
                individual.registrant_id,
                r"^IND_[a-zA-Z0-9]{8}$",
                "Individual should have unique registrant id start with "
                "`IND_` and following by 8 characters.",
            )
            for char in EXCLUDED_CHARACTERS:
                self.assertNotIn(
                    char,
                    individual.registrant_id.split("_")[-1],
                    "Excluded characters should not be exist in unique registrant_id",
                )

    @mute_logger("odoo.sql_db")
    def test_04_compute_registrant_id_unique_violation(self):
        with self.assertRaises(UniqueViolation):
            self._test_individuals[0].write(
                {
                    "registrant_id": self._test_individuals[1].registrant_id,
                }
            )
            self.env.cr.commit()
