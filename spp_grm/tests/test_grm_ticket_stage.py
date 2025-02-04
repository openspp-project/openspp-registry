from odoo.tests.common import TransactionCase


class SPPGRMTicketStageTests(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage = cls.env["spp.grm.ticket.stage"].create(
            {
                "name": "Test Stage",
                "sequence": 1,
                "active": True,
            }
        )

    def stage_creation(self):
        new_stage = self.env["spp.grm.ticket.stage"].create(
            {
                "name": "New Stage",
                "sequence": 2,
                "active": False,
            }
        )
        self.assertEqual(new_stage.name, "New Stage")

    def stage_sequence_order(self):
        self.assertEqual(self.stage.sequence, 1)

    def stage_active_status(self):
        self.assertTrue(self.stage.active)

    def stage_unattended_status(self):
        self.assertFalse(self.stage.unattended)

    def stage_closed_status(self):
        self.assertFalse(self.stage.closed)

    def stage_folded_status(self):
        self.assertFalse(self.stage.fold)

    def stage_onchange_closed(self):
        self.stage.write({"closed": True})
        self.assertFalse(self.stage.fold)
