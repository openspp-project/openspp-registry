import logging

from odoo import _, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPBaseImport(models.TransientModel):
    _inherit = "base_import.import"

    def execute_import(self, fields, columns, options, dryrun=False):
        if self.res_model == "res.partner":
            with_is_group = False
            if "is_group" in fields:
                with_is_group = True
            if "default_is_group" in self.env.context:
                if self.env.context["default_is_group"]:
                    with_is_group = True
            if "default_kind" in self.env.context:
                if self.env.context["default_kind"] == self.env.ref("spp_farmer_registry_base.kind_farm").id:
                    with_is_group = True
                else:
                    with_is_group = False

            if with_is_group and not ("farmer_given_name" in fields and "farmer_family_name" in fields):
                raise ValidationError(_("farmer_given_name and farmer_family_name must be present in the excel file."))

        return super().execute_import(fields, columns, options, dryrun=dryrun)
