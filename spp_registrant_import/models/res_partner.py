from odoo import _, api, fields, models


class Registrant(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "spp.unique.id"]

    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name",
        store=True,
    )
    spp_id = fields.Char(readonly=False)

    @api.onchange("is_group", "family_name", "given_name", "addl_name")
    def name_change(self):
        pass

    @api.depends(
        "is_registrant",
        "is_group",
        "family_name",
        "given_name",
        "addl_name",
    )
    def _compute_name(self):
        for rec in self:
            if not rec.is_registrant or rec.is_group:
                continue
            name = []
            if rec.family_name:
                name.append(rec.family_name)
            if rec.given_name:
                name.append(rec.given_name)
            if rec.addl_name:
                name.append(self.addl_name)
            rec.name = ", ".join(name).upper()

    def _inverse_name(self):
        for rec in self:
            if not rec.is_registrant or rec.is_group:
                continue
            name = list(map(lambda i: i, self.name.split(", ")))
            if len(name) == 1:
                rec.given_name = name[0]
            elif len(name) == 2:
                rec.family_name = name[0]
                # Added to resolve the issue of names not from import
                # That the given_name is appended with the addl_name
                if rec.given_name and rec.addl_name:
                    name_check = rec.given_name + " " + rec.addl_name
                    if not name_check.lower() == name[1].lower():
                        rec.given_name = name[1]
                else:
                    rec.given_name = name[1]
            else:
                rec.family_name = name[0]
                rec.given_name = name[1]
                rec.addl_name = name[2]

    def _get_spp_id_prefix(self):
        if not self.is_registrant:
            return ""
        if self.is_group:
            return "GRP"
        return "IND"

    def _get_match_spp_id_pattern(self):
        if not self.is_registrant:
            return ""
        if self.is_group:
            return r"^GRP_[0-9A-Z]{8}$"
        return r"^IND_[0-9A-Z]{8}$"

    @api.model
    def get_import_templates(self):
        context = self.env.context
        if context.get("default_is_registrant"):
            if context.get("default_is_group"):
                import_templates = [
                    {
                        "label": _("Import Template for Groups"),
                        "template": "/spp_registrant_import/static/xls/group_registry.xlsx",
                    }
                ]
            else:
                import_templates = [
                    {
                        "label": _("Import Template for Individuals"),
                        "template": "/spp_registrant_import/static/xls/individual_registry.xlsx",
                    }
                ]

            return import_templates
        return super().get_import_templates()
