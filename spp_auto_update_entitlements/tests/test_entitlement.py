from odoo import fields

from .common import Common


class TestEntitlement(Common):
    def test_compute_balance(self):
        self.entitlement._compute_balance()

        self.assertEqual(self.entitlement.entitlement_balance, self.entitlement.initial_amount)

        self.entitlement_transaction_1 = self.env["spp.entitlement.transactions"].create(
            {
                "entitlement_id": self.entitlement.id,
                "amount_charged_by_service_point": 100.00,
                "transaction_type": "VOID",
                "user_id": self.env.ref("base.user_root").id,
                "transaction_uuid": "test-uuid",
                "currency_id": self.env.ref("base.USD").id,
                "timestamp_transaction_created": fields.Datetime.now(),
            }
        )

        self.assertEqual(
            self.entitlement.entitlement_balance,
            self.entitlement.initial_amount + self.entitlement_transaction_1.amount_charged_by_service_point,
        )

        self.entitlement_transaction_2 = self.env["spp.entitlement.transactions"].create(
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
        self.assertEqual(
            self.entitlement.entitlement_balance,
            (
                self.entitlement.initial_amount
                + self.entitlement_transaction_1.amount_charged_by_service_point
                - self.entitlement_transaction_2.amount_charged_by_service_point
            ),
        )
