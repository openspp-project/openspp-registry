from odoo.tests.common import TransactionCase


class TestUserRole(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.center_area = cls.env["spp.area"].create(
            {
                "name": "Test Center Area",
                "draft_name": "Test Center Area",
            }
        )

        default_user = cls.env.ref("base.default_user")
        default_group_user = cls.env.ref("base.group_user")

        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "role_line_ids": [
                    (0, 0, {"role_id": default_user.id, "local_area_id": cls.center_area.id}),
                    (0, 0, {"role_id": default_group_user.id, "local_area_id": cls.center_area.id}),
                ],
            }
        )

    def test_set_groups_from_roles(self):
        result = self.user.set_groups_from_roles()
        self.assertTrue(result)

        result = self.user.set_groups_from_roles(force=True)
        self.assertTrue(result)

        self.user.set_groups_from_roles()
        self.assertIn(self.env.ref("base.group_user").id, self.user.groups_id.ids)
        self.assertIn(self.env.ref("base.group_no_one").id, self.user.groups_id.ids)

        self.user.write({"role_line_ids": [(5)]})
        self.user.set_groups_from_roles()
        self.assertIn(self.env.ref("base.group_user").id, self.user.groups_id.ids)
        self.assertIn(self.env.ref("base.group_no_one").id, self.user.groups_id.ids)

    def test_default_role_lines(self):
        default_user = self.env.ref("base.default_user", raise_if_not_found=False)
        default_user.role_line_ids = [
            (0, 0, {"role_id": self.env.ref("base.default_user").id}),
            (0, 0, {"role_id": self.env.ref("base.group_user").id}),
        ]
        default_values = self.env["res.users"]._default_role_lines()

        self.assertTrue(bool(default_values))
        self.assertEqual(len(default_values), 2)
        self.assertEqual(default_values[0]["role_id"], self.env.ref("base.default_user").id)
        self.assertEqual(default_values[1]["role_id"], self.env.ref("base.group_user").id)
        self.assertFalse(default_values[0]["local_area_id"])
        self.assertFalse(default_values[1]["local_area_id"])
        self.assertTrue(default_values[0]["is_enabled"])
        self.assertTrue(default_values[1]["is_enabled"])
        self.assertFalse(default_values[0]["date_from"])
        self.assertFalse(default_values[1]["date_from"])
        self.assertFalse(default_values[0]["date_to"])
        self.assertFalse(default_values[1]["date_to"])

    def test_compute_center_area_ids(self):
        self.user._compute_center_area_ids()

        self.assertEqual(len(self.user.center_area_ids), 1)
        self.assertEqual(self.user.center_area_ids, self.center_area)
