from odoo.tests import TransactionCase


class TestCreateEventWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner", "is_registrant": True, "is_group": True})
        cls.event_data_wizard = cls.env["spp.create.event.wizard"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def test_compute_program_membership_id_domain(self):
        self.event_data_wizard._compute_program_membership_id_domain()
        expected_result = f'[["partner_id", "=", {self.partner.id}]]'
        self.assertEqual(
            self.event_data_wizard.program_membership_id_domain,
            expected_result,
        )

    def test_get_event_data_vals(self):
        data_vals = self.event_data_wizard.get_event_data_vals()

        self.assertEqual(data_vals["model"], "default")
        self.assertEqual(data_vals["partner_id"], self.partner.id)
        self.assertEqual(data_vals["registrar"], False)
        self.assertEqual(data_vals["collection_date"], self.event_data_wizard.collection_date)
        self.assertEqual(data_vals["expiry_date"], False)
        self.assertEqual(data_vals["program_membership_id"], False)
