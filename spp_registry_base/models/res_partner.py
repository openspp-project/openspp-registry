from odoo import _, api, models


class Registrant(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_import_templates(self):
        context = self.env.context
        if context.get("default_is_registrant"):
            if context.get("default_is_group"):
                import_templates = [
                    {
                        "label": _("Import Template for Groups"),
                        "template": "/spp_registry/static/xls/group_registry.xlsx",
                    }
                ]
            else:
                import_templates = [
                    {
                        "label": _("Import Template for Individuals"),
                        "template": "/spp_registry/static/xls/individual_registry.xlsx",
                    }
                ]

            return import_templates
        return super().get_import_templates()
