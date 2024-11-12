from odoo.tests.common import TransactionCase


class TestOpenSPPResPartnerCustom(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.view_group_id = cls.env.ref("g2p_registry_group.view_groups_form").id
        cls.view_group_action_id = cls.env.ref("g2p_registry_group.action_groups_list").id

        cls.view_individual_id = cls.env.ref("g2p_registry_individual.view_individuals_form").id
        cls.view_individual_action_id = cls.env.ref("g2p_registry_individual.action_individuals_list").id

    def test_get_view_group(self):
        options = {"action_id": self.view_group_action_id, "load_filters": True, "toolbar": True}
        arch, view = self.env["res.partner"]._get_view(self.view_group_id, "form", **options)

        self.assertEqual(len(arch.xpath("//page[@name='indicators']")), 1)
        self.assertEqual(len(arch.xpath("//page[@name='additional_details']")), 0)

    def test_get_view_individual(self):
        options = {"action_id": self.view_individual_action_id, "load_filters": True, "toolbar": True}
        arch, view = self.env["res.partner"]._get_view(self.view_individual_id, "form", **options)

        self.assertEqual(len(arch.xpath("//page[@name='indicators']")), 0)
        self.assertEqual(len(arch.xpath("//page[@name='additional_details']")), 1)

    def test_get_view_no_options(self):
        arch, view = self.env["res.partner"]._get_view(self.view_individual_id, "form")

        self.assertEqual(len(arch.xpath("//page[@name='indicators']")), 0)
        self.assertEqual(len(arch.xpath("//page[@name='additional_details']")), 1)
