from odoo.tests import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestSppStarter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sgd = cls.env.ref("base.SGD").id
        cls.test_record = cls.env["spp.starter"].create(
            {
                "org_name": "Newlogic",
                "org_address": "160 Robinson Rd #14-04 SBF Centre Singapore 068914",
                "org_phone": "+65 3138 4664",
                "org_currency_id": cls.sgd,
            }
        )

    def test_01_action_last_state(self):
        self.test_record.state = "5"
        self.test_record.action_last_state()
        self.assertEqual(self.test_record.state, "4")
        self.test_record.action_last_state()
        self.assertEqual(self.test_record.state, "3")
        self.test_record.action_last_state()
        self.assertEqual(self.test_record.state, "2")
        self.test_record.action_last_state()
        self.assertEqual(self.test_record.state, "1")
        self.test_record.action_last_state()
        self.assertEqual(self.test_record.state, "0")
        self.test_record.action_last_state()
        self.assertEqual(self.test_record.state, "0")

    def test_02_action_next_state(self):
        self.test_record.action_next_state()
        self.assertEqual(self.test_record.state, "1")
        self.test_record.action_next_state()
        self.assertEqual(self.test_record.state, "2")
        self.test_record.action_next_state()
        self.assertEqual(self.test_record.state, "3")
        self.test_record.action_next_state()
        self.assertEqual(self.test_record.state, "4")
        self.test_record.action_next_state()
        self.assertEqual(self.test_record.state, "5")
        self.test_record.action_next_state()
        self.assertEqual(self.test_record.state, "5")

    def test_03_reopen(self):
        res = self.test_record._reopen()
        self.assertEqual(type(res), dict)
        for key in ("name", "type", "res_model", "res_id", "view_mode", "target"):
            self.assertIn(key, res.keys())
        self.assertEqual(res["name"], "SPP Starter")
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "spp.starter")
        self.assertEqual(res["res_id"], self.test_record.id)
        self.assertEqual(res["view_mode"], "form")
        self.assertEqual(res["target"], "new")

    def test_04_remove_fake_apps_menu(self):
        self.test_record._remove_fake_apps_menu()
        show_spp_starter = self.env["ir.config_parameter"].sudo().get_param("spp_starter.show_spp_starter")
        self.assertFalse(safe_eval(show_spp_starter))

    def test_05_remove_default_products_if_needed(self):
        self.test_record.conducting_inkind_transfer = "yes"
        if "product.template" not in self.env:
            self.test_record._remove_default_products_if_needed()
        fake_product_template = self.env["product.template"].create(
            {
                "name": "Fake Test Product",
            }
        )
        self.assertTrue(fake_product_template.active)
        self.test_record._remove_default_products_if_needed()
        self.assertFalse(fake_product_template.active)

    # def test_07_adjust_main_company_details(self):
    #     if "account.move.line" in self.env:
    #         self.env["account.move.line"].search([]).with_context(force_delete=True).unlink()
    #     self.test_record._adjust_main_company_details()
    #     company = self.env.company
    #     self.assertEqual(company.name, self.test_record.org_name)
    #     self.assertEqual(company.street, self.test_record.org_address)
    #     self.assertEqual(company.phone, self.test_record.org_phone)
    #     self.assertEqual(company.currency_id, self.test_record.org_currency_id)

    # def test_08_install_modules(self):
    #     def find_module(module_name):
    #         return self.env.ref(f"base.module_{module_name}", raise_if_not_found=False)

    #     spp_theme = find_module("theme_openspp_muk")
    #     self.assertIn(spp_theme, self.test_record._install_modules())
    #     gp2_individual = find_module("g2p_registry_individual")
    #     gp2_group = find_module("g2p_registry_group")
    #     self.test_record.managing_target = "group"
    #     self.assertIn(gp2_group, self.test_record._install_modules())
    #     self.test_record.managing_target = "individual"
    #     self.assertIn(gp2_individual, self.test_record._install_modules())
