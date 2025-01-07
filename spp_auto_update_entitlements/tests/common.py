from odoo import fields
from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.program = cls.env["g2p.program"].create({"name": "Test Program"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": cls.program.id,
                "start_date": fields.Datetime.now(),
                "end_date": fields.Datetime.now(),
            }
        )

        cls.cycle_manager = cls.env["g2p.cycle.manager.default"].create(
            {
                "name": "Test Cycle Manager",
                "program_id": cls.program.id,
            }
        )

        cls.entitlement = cls.env["g2p.entitlement"].create(
            {
                "program_id": cls.program.id,
                "partner_id": cls.partner.id,
                "cycle_id": cls.cycle.id,
                "state": "draft",
                "initial_amount": 100.00,
            }
        )
