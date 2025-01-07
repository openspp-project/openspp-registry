from datetime import timedelta

from odoo import fields

from .common import Common


class TestCycle(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.entitlement_transaction = cls.env["spp.entitlement.transactions"].create(
            {
                "entitlement_id": cls.entitlement.id,
                "amount_charged_by_service_point": 100.00,
                "transaction_type": "VOID",
                "user_id": cls.env.ref("base.user_root").id,
                "transaction_uuid": "test-uuid",
                "currency_id": cls.env.ref("base.USD").id,
                "timestamp_transaction_created": fields.Datetime.now(),
            }
        )

    def test_compute_is_expired(self):
        self.cycle._compute_is_expired()
        self.assertTrue(self.cycle.is_expired)

        self.cycle.end_date = fields.Datetime.now() + timedelta(days=1)
        self.cycle._compute_is_expired()
        self.assertFalse(self.cycle.is_expired)

    def test_mark_ended(self):
        self.cycle_manager.mark_ended(self.cycle)
        self.assertEqual(self.cycle.state, "ended")

    def test_check_cycle_entitlements(self):
        self.cycle_manager.check_cycle_entitlements(self.cycle)
        self.assertEqual(self.cycle.entitlement_ids.mapped("state"), ["draft"])

    def test_check_entitlements_transactions(self):
        state = self.cycle_manager.check_entitlements_transactions(self.entitlement)
        self.assertEqual(state, "draft")

        self.env["spp.entitlement.transactions"].create(
            {
                "entitlement_id": self.entitlement.id,
                "amount_charged_by_service_point": 300.00,
                "transaction_type": "PURCHASE",
                "user_id": self.env.ref("base.user_root").id,
                "transaction_uuid": "test-uuid2",
                "currency_id": self.env.ref("base.USD").id,
                "timestamp_transaction_created": fields.Datetime.now(),
            }
        )
        self.entitlement._compute_balance()
        state = self.cycle_manager.check_entitlements_transactions(self.entitlement)
        self.assertEqual(state, "parrdpd2ben")

        self.env["spp.entitlement.transactions"].create(
            {
                "entitlement_id": self.entitlement.id,
                "amount_charged_by_service_point": 100.00,
                "transaction_type": "VOID",
                "user_id": self.env.ref("base.user_root").id,
                "transaction_uuid": "test-uuid3",
                "currency_id": self.env.ref("base.USD").id,
                "timestamp_transaction_created": fields.Datetime.now(),
            }
        )
        state = self.cycle_manager.check_entitlements_transactions(self.entitlement)
        self.assertEqual(state, "rdpd2ben")
