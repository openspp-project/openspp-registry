from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError

from .common import Common


class TestChangeRequests(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_change_request = cls._create_change_request()

    def test_01_create(self):
        self.assertEqual(
            self._test_change_request.assign_to_id,
            self.env.user,
            "Creating user should be default assignee!",
        )

    def test_02_unlink_raise_error(self):
        with self.assertRaisesRegex(UserError, "Only draft change requests can be deleted by its creator."):
            self._test_change_request.with_user(2).unlink()
        self._test_change_request.state = "pending"
        with self.assertRaisesRegex(UserError, "Only draft change requests can be deleted by its creator."):
            self._test_change_request.unlink()

    def test_03_unlink(self):
        self._test_change_request.unlink()
        remaining_change_request = self.env["spp.change.request"].search([("request_type", "=", "request_type")])
        self.assertCountEqual(
            remaining_change_request.ids,
            [],
            "Draft change request should unlinkable by its creator!",
        )

    def test_04_compute_applicant_id_domain(self):
        self.assertEqual(
            self._test_change_request.applicant_id_domain,
            [("id", "=", 0)],
            "Without registrant, applicant selections should not be available!",
        )
        self._test_change_request.registrant_id = self._test_group
        self.assertEqual(
            self._test_change_request.applicant_id_domain,
            [
                (
                    "id",
                    "in",
                    self._test_change_request.registrant_id.group_membership_ids.individual.ids,
                )
            ],
            "With registrant, applicant selection should be available!",
        )

    def test_05_assign_to_user(self):
        admin = self.env.ref("base.user_admin")
        self._test_change_request.assign_to_user(admin)
        self.assertEqual(
            self._test_change_request.assign_to_id,
            admin,
            "Admin should be the one who assigned to this CR!",
        )
        self._test_change_request.state = "pending"
        with self.assertRaisesRegex(UserError, "^.*not have any validation sequence defined.$"):
            self._test_change_request.assign_to_user(self.env.user)

    def test_06_onchange_scan_qr_code_details(self):
        self._test_change_request.qr_code_details = '{"qrcode": "-T-E-S-T-Q-R-C-O-D-E-"}'
        with self.assertRaisesRegex(UserError, "^.*no group found with the ID number from the QR Code scanned.$"):
            self._test_change_request._onchange_scan_qr_code_details()
        self.env["g2p.reg.id"].create(
            {
                "partner_id": self._test_group.id,
                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
                "value": "-T-E-S-T-Q-R-C-O-D-E-",
            }
        )
        self._test_change_request._onchange_scan_qr_code_details()
        self.assertEqual(
            self._test_change_request.registrant_id,
            self._test_group,
            "Registrant on CR should be test group!",
        )

    @patch(
        "odoo.addons.phone_validation.tools.phone_validation.phone_parse",
        return_value="1",
    )
    def test_07_open_request_detail(self, phone_parse):
        with self.assertRaisesRegex(UserError, "Phone No. is required."):
            self._test_change_request.open_request_detail()
        self._test_change_request.applicant_phone = "+9647001234567"
        res = self._test_change_request.open_request_detail()
        self.assertListEqual(
            [res.get("type"), res.get("tag"), res.get("params", {}).get("type")],
            ["ir.actions.client", "display_notification", "danger"],
            "Request Type ID not existed, client should display error notification!",
        )

    def test_08_cancel_error(self):
        with self.assertRaisesRegex(UserError, "^.*request to be cancelled must be in draft.*$"):
            self._test_change_request.state = "validated"
            self._test_change_request._cancel(self._test_change_request)

    def test_09_cancel(self):
        self.assertListEqual(
            [
                self._test_change_request.state,
                self._test_change_request.cancelled_by_id.id,
                self._test_change_request.date_cancelled,
            ],
            ["draft", False, False],
            "Draft CR should not have cancelling info.!",
        )
        self._test_change_request._cancel(self._test_change_request)
        self.assertListEqual(
            [
                self._test_change_request.state,
                self._test_change_request.cancelled_by_id,
            ],
            ["cancelled", self.env.user],
            "Cancelled CR should have cancelling info.!",
        )
        self.assertLessEqual(
            self._test_change_request.date_cancelled,
            fields.Datetime.now(),
            "Cancelled CR should have date cancelled info.!",
        )

    def test_10_check_user_error(self):
        self._test_change_request.assign_to_id = None
        with self.assertRaisesRegex(UserError, "^.*no user assigned.*$"):
            self._test_change_request._check_user(process="Apply")

    def test_11_check_user(self):
        with self.assertRaisesRegex(UserError, "^You are not allowed.*$"):
            self._test_change_request.with_user(2)._check_user(process="Apply")
        self.assertTrue(
            self._test_change_request._check_user(process="Apply"),
            "Change request creator / assignee should have access!",
        )
