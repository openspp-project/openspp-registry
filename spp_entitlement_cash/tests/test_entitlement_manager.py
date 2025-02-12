import logging
from datetime import date
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase

_logger = logging.getLogger(__name__)


class TestEntitlementManager(TransactionCase):
    GROUP_KIND_HOUSEHOLD = "g2p_registry_group.group_kind_household"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registrants = cls.env["res.partner"].create(
            [
                {
                    "name": "Registrant 1 [TEST]",
                    "is_registrant": True,
                    "is_group": True,
                },
                {
                    "name": "Registrant 2 [TEST]",
                    "is_registrant": True,
                    "is_group": True,
                },
            ]
        )
        cls.individuals = cls.env["res.partner"].create(
            [
                {
                    "name": "Individual 1 [TEST]",
                    "is_registrant": True,
                    "is_group": False,
                },
                {
                    "name": "Individual 2 [TEST]",
                    "is_registrant": True,
                    "is_group": False,
                },
            ]
        )
        cls.env["g2p.group.membership"].create(
            [
                {
                    "individual": cls.individuals[0].id,
                    "group": cls.registrants[0].id,
                },
                {
                    "individual": cls.individuals[1].id,
                    "group": cls.registrants[0].id,
                },
            ]
        )
        cls.program = cls.env["g2p.program"].create(
            {
                "name": "Program 1 [TEST]",
                "program_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.registrants[0].id,
                            "state": "enrolled",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.registrants[-1].id,
                            "state": "enrolled",
                        },
                    ),
                ],
            }
        )
        cls.program.create_journal()
        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Cycle 1 [TEST]",
                "program_id": cls.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )
        cls._cash_entitlement_manager = cls.env["g2p.program.entitlement.manager.cash"].create(
            {
                "name": "Entitlement Manager Cash 1 [TEST]",
                "program_id": cls.program.id,
            }
        )

    def _funding(self):
        return self.env["g2p.program.fund"].create(
            {
                "name": "PF-2023-000001",
                "program_id": self.program.id,
                "amount": 50_000_000.0,
                "state": "posted",
            }
        )

    def create_entitlement(self):
        return self.env["g2p.entitlement"].create(
            {
                "partner_id": self.registrants[0].id,
                "cycle_id": self.cycle.id,
                "valid_from": fields.Date.today(),
                "initial_amount": 5.0,
            }
        )

    def test_01_prepare_entitlements(self):
        # Test case 1: No items entered
        with self.assertRaisesRegex(UserError, "no items entered for this"):
            self._cash_entitlement_manager.prepare_entitlements(self.cycle, self.program.program_membership_ids)

        # Test case 2: Basic entitlement creation
        self._cash_entitlement_manager.write(
            {
                "entitlement_item_ids": [(0, 0, {"amount": 5.0})],
            }
        )
        before_entitlement = self.env["g2p.entitlement"].search([])
        self.assertFalse(before_entitlement.ids, "Start without entitlement!")
        self._cash_entitlement_manager.prepare_entitlements(self.cycle, self.program.program_membership_ids)
        after_entitlement = self.env["g2p.entitlement"].search([])
        self.assertTrue(bool(after_entitlement.ids), "Entitlement should be created!")

    def test_02_set_pending_validation_entitlements(self):
        entitlement = self.create_entitlement()
        entitlement.state = "draft"
        self._cash_entitlement_manager.set_pending_validation_entitlements(self.cycle)
        self.assertEqual(
            entitlement.state,
            "pending_validation",
            "Entitlement now should be pending validation!",
        )

    @patch("odoo.fields.Date.today")
    def test_03_validate_entitlements(self, mock_today):
        mock_today.__name__ = "mock_today"
        mock_today.return_value = date(2023, 5, 23)
        entitlement = self.create_entitlement()

        # Test case 1: No funding
        res = self._cash_entitlement_manager.validate_entitlements(self.cycle)
        self.assertEqual(
            res["params"]["type"],
            "danger",
            "Should display danger notification [no fund]!",
        )

        # Test case 2: With funding and transfer fee
        self._funding()
        entitlement.write({"transfer_fee": 1.0})
        res = self._cash_entitlement_manager.validate_entitlements(self.cycle)
        self.assertEqual(res["params"]["type"], "success", "Should display success notification!")
        self.assertEqual(entitlement.state, "approved", "Entitlement should now be approved!")
        self.assertTrue(entitlement.service_fee_disbursement_id, "Service fee payment should be created!")
        self.assertEqual(entitlement.service_fee_disbursement_id.amount, 1.0, "Service fee amount should be correct!")

        # Test case 3: Invalid state validation
        entitlement2 = self.create_entitlement()
        entitlement2.state = "approved"

    def test_04_cancel_entitlements(self):
        entitlement = self.create_entitlement()
        self._cash_entitlement_manager.cancel_entitlements(self.cycle)
        self.assertEqual(entitlement.state, "cancelled", "Entitlement should now cancelled!")

    def test_05_open_entitlements_form(self):
        res = self._cash_entitlement_manager.open_entitlements_form(self.cycle)
        for key in ["res_model", "type", "domain"]:
            self.assertIn(key, res.keys(), f"Key `{key}` is missing from return action!")
        self.assertEqual(res["res_model"], "g2p.entitlement")
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["domain"], [("cycle_id", "=", self.cycle.id)])

    def test_06_open_entitlement_form(self):
        entitlement = self.create_entitlement()
        res = self._cash_entitlement_manager.open_entitlement_form(entitlement)
        for key in ["res_model", "type", "target", "res_id", "view_mode"]:
            self.assertIn(key, res.keys(), f"Key `{key}` is missing from return action!")
        self.assertEqual(res["res_model"], "g2p.entitlement")
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["target"], "new")
        self.assertEqual(res["res_id"], entitlement.id)
        self.assertEqual(res["view_mode"], "form")

    def test_check_subsidy(self):
        """Test the _check_subsidy method of cash entitlement manager"""
        # Create a cash entitlement manager with max_amount = 100

        # Test when amount is less than max_amount
        self.assertEqual(self._cash_entitlement_manager._check_subsidy(50.0), 50.0)

        # Test when amount is greater than max_amount
        self._cash_entitlement_manager.max_amount = 100.0
        self.assertEqual(self._cash_entitlement_manager._check_subsidy(150.0), 100.0)

        # Test when max_amount is 0 (no limit)
        self._cash_entitlement_manager.max_amount = 0.0
        self.assertEqual(self._cash_entitlement_manager._check_subsidy(150.0), 150.0)
