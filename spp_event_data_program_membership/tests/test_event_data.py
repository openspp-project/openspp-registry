from odoo.tests import TransactionCase


class TestEventData(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "is_registrant": True,
                "is_group": True,
            }
        )

        cls.event_data_1 = cls.env["spp.event.data"].create(
            {
                "partner_id": cls.partner_1.id,
                "model": "spp.event.agri.ds.hot",
            }
        )

    def test_compute_program_membership_id_domain(self):
        self.event_data_1._compute_program_membership_id_domain()
        expected_result = f'[["partner_id", "=", {self.partner_1.id}]]'
        self.assertEqual(
            self.event_data_1.program_membership_id_domain,
            expected_result,
        )
