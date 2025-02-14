from odoo import fields
from odoo.exceptions import UserError

from .common import Common


class TestChangeRequestBase(Common):
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

    def test_07_open_request_detail(self):
        res = self._test_change_request.open_request_detail()
        self.assertListEqual(
            [res.get("type"), res.get("tag"), res.get("params", {}).get("type")],
            ["ir.actions.client", "display_notification", "danger"],
            "Request Type ID does not exist, client should display error notification!",
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
