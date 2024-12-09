from odoo import fields
from odoo.tests import TransactionCase


class TestManualEligibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "name": "Registrant 1 [MANUAL ELIGIBILITY TEST]",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "name": "Registrant 2 [MANUAL ELIGIBILITY TEST]",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.program = cls.env["g2p.program"].create({"name": "Program 1 [MANUAL ELIGIBILITY TEST]"})
        cls.manual_eligibility_manager = cls.env["g2p.program_membership.manager.default"].create(
            {
                "name": "Eligibility Manager Cash 1 [MANUAL ELIGIBILITY TEST]",
                "is_manual_eligibility": True,
                "eligibility_domain": None,
                "program_id": cls.program.id,
            }
        )

    def test_01_check_if_manual_eligibility(self):
        self.program._compute_is_manual_eligibility()
        self.assertEqual(self.program.is_manual_eligibility, True, "Correct value")
        self.assertEqual(len(self.program.program_membership_ids), 0, "Start without members")
        vals = [
            {
                "partner_id": self.registrant_1.id,
                "program_id": self.program.id,
                "state": "enrolled",
                "enrollment_date": fields.Datetime.now(),
            },
            {
                "partner_id": self.registrant_2.id,
                "program_id": self.program.id,
                "state": "enrolled",
                "enrollment_date": fields.Datetime.now(),
            },
        ]
        self.env["g2p.program_membership"].create(vals)
        self.assertEqual(len(self.program.program_membership_ids), 2, "Finish with members")
        self.program.program_membership_ids[0]._compute_is_manual_eligibility()
        self.assertEqual(self.program.program_membership_ids[0].is_manual_eligibility, True, "Correct value")
