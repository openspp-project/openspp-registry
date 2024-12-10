from odoo.tests import TransactionCase


class TestRegistrant(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_get_import_templates(self):
        import_template = self.env["res.partner"].get_import_templates()
        self.assertEqual(
            import_template,
            [{"label": "Import Template for Customers", "template": "/base/static/xls/res_partner.xlsx"}],
        )

        import_template = self.env["res.partner"].with_context(default_is_registrant=True).get_import_templates()
        self.assertEqual(
            import_template,
            [
                {
                    "label": "Import Template for Individuals",
                    "template": "/spp_registry/static/xls/individual_registry.xlsx",
                }
            ],
        )

        import_template = (
            self.env["res.partner"]
            .with_context(default_is_registrant=True, default_is_group=True)
            .get_import_templates()
        )
        self.assertEqual(
            import_template,
            [
                {
                    "label": "Import Template for Groups",
                    "template": "/spp_registry/static/xls/group_registry.xlsx",
                }
            ],
        )
