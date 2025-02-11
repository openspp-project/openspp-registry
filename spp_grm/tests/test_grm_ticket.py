from odoo import fields
from odoo.tests.common import TransactionCase


class SPPGRMTicketTests(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket_stage_open = cls.env["spp.grm.ticket.stage"].create({"name": "Open", "closed": False})
        cls.ticket_stage_closed = cls.env["spp.grm.ticket.stage"].create({"name": "Closed", "closed": True})
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 1",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
            }
        )
        cls.ticket = cls.env["spp.grm.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Test Description",
                "partner_id": cls.partner_1.id,
                "stage_id": cls.ticket_stage_open.id,
            }
        )

    def test_ticket_creation_number_generation(self):
        """Test creation with default '/' number triggers number generation."""
        new_ticket = self.env["spp.grm.ticket"].create(
            {
                "name": "New Ticket",
                "description": "New Description",
                "partner_id": self.partner_2.id,
                "number": "/",
            }
        )
        self.assertNotEqual(new_ticket.number, "/")

    def test_ticket_creation_user_assignment(self):
        """Test creation where user_id is set but assigned_date is not."""
        new_ticket = self.env["spp.grm.ticket"].create(
            {
                "name": "Assigned Ticket",
                "description": "Assigned Description",
                "partner_id": self.partner_2.id,
                "user_id": self.env.ref("base.user_admin").id,
            }
        )
        self.assertEqual(new_ticket.user_id, self.env.ref("base.user_admin"))
        self.assertIsNotNone(new_ticket.assigned_date)

    def test_ticket_copy_number_generation(self):
        """Test copying a ticket generates a new number."""
        copied_ticket = self.ticket.copy()
        self.assertNotEqual(copied_ticket.number, self.ticket.number)

    def test_ticket_copy_custom_number(self):
        """Test copying a ticket with a provided number in default."""
        copied_ticket = self.ticket.copy(default={"number": "CUSTOM123"})
        self.assertEqual(copied_ticket.number, "CUSTOM123")

    def test_ticket_write_stage_update(self):
        """Test writing stage_id updates last_stage_update and closed_date (if closed)."""
        now = fields.Datetime.now()

        self.ticket.write({"stage_id": self.ticket_stage_closed.id})
        self.assertEqual(self.ticket.stage_id, self.ticket_stage_closed)
        self.assertEqual(self.ticket.closed_date.date(), now.date())
        self.assertEqual(self.ticket.last_stage_update.date(), now.date())

    def test_ticket_write_user_assignment(self):
        """Test writing user_id updates assigned_date."""
        now = fields.Datetime.now()

        self.ticket.write({"user_id": self.env.ref("base.user_admin").id})
        self.assertEqual(self.ticket.user_id, self.env.ref("base.user_admin"))
        self.assertEqual(self.ticket.assigned_date.date(), now.date())

    def test_ticket_write_no_stage_or_user_change(self):
        """Test that writing without stage_id or user_id does not alter dates."""
        original_last_stage_update = self.ticket.last_stage_update
        original_assigned_date = self.ticket.assigned_date

        self.ticket.write({"name": "Updated Ticket Name"})
        self.assertEqual(self.ticket.last_stage_update, original_last_stage_update)
        self.assertEqual(self.ticket.assigned_date, original_assigned_date)
