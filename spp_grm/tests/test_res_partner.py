from odoo.tests.common import TransactionCase


class ResPartnerTicketTests(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.ticket = cls.env["spp.grm.ticket"].create(
            {
                "name": "Test Ticket",
                "partner_id": cls.partner.id,
            }
        )

    def partner_ticket_relation(self):
        self.assertIn(self.ticket, self.partner.grm_ticket_ids)

    def partner_ticket_count(self):
        self.assertEqual(self.partner.grm_ticket_count, 1)

    def partner_active_ticket_count(self):
        self.assertEqual(self.partner.grm_ticket_active_count, 1)

    def partner_ticket_count_string(self):
        self.assertEqual(self.partner.grm_ticket_count_string, "1 / 1")

    def partner_action_view_grm_tickets(self):
        action = self.partner.action_view_grm_tickets()
        self.assertEqual(action["res_model"], "spp.grm.ticket")
        self.assertEqual(action["domain"], [("partner_id", "child_of", self.partner.id)])
