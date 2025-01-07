from odoo.tests import TransactionCase


class TestProgramMembership(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.program = cls.env["g2p.program"].create({"name": "Test Program"})
        cls.membership = cls.env["g2p.program_membership"].create(
            {
                "partner_id": cls.partner.id,
                "program_id": cls.program.id,
                "state": "enrolled",
            }
        )

    def test_compute_display_name(self):
        self.membership._compute_display_name()
        expected_result = f"[{self.program.name}] {self.partner.name}"
        self.assertEqual(self.membership.display_name, expected_result)
