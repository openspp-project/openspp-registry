# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPImportMatch(models.Model):
    _name = "spp.import.match"
    _description = "Import Matching"
    _order = "sequence, name"

    name = fields.Char()
    sequence = fields.Integer(index=True)
    overwrite_match = fields.Boolean()
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
        domain=[("transient", "=", False)],
        help="Model for Import Matching",
    )
    model_name = fields.Char(related="model_id.model")
    model_description = fields.Char(related="model_id.name")
    field_ids = fields.One2many(
        "spp.import.match.fields",
        "match_id",
        string="Fields",
        required=True,
        help="Fields to Match in Importing",
    )

    @api.onchange("model_id")
    def _onchange_model_id(self):
        for rec in self:
            rec.field_ids = None

    @api.model
    def _match_find(self, model, converted_row, imported_row):
        usable, field_to_match = self._usable_rules(model._name, converted_row)
        usable = self.browse(usable)
        for combination in usable:
            combination_valid = True
            domain = list()
            for field in combination.field_ids:
                if field.conditional:
                    if imported_row[field.name] != field.imported_value:
                        combination_valid = False
                        break
                if field.field_id.name in converted_row:
                    row_value = converted_row[field.field_id.name]
                    field_value = field.field_id.name
                    add_to_domain = True
                    if field.sub_field_id:
                        tuple_val = row_value[0][2]
                        add_to_domain = False
                        if field.sub_field_id.name in tuple_val:
                            row_value = tuple_val[field.sub_field_id.name]
                            add_to_domain = True
                            field_value = field.field_id.name + "." + field.sub_field_id.name
                    if add_to_domain:
                        domain.append((field_value, "=", row_value))
            if not combination_valid:
                continue
            match = model.search(domain)
            if len(match) == 1:
                return match
            elif len(match) > 1:
                raise ValidationError(_("Multiple matches found for '%s'!" % match[0].name))

        return model

    @api.model
    def _usable_rules(self, model_name, fields, option_config_ids=False):
        result = self
        domain = [("model_name", "=", model_name)]
        if option_config_ids and isinstance(option_config_ids, list):
            domain.append(("id", "in", option_config_ids))
        available = self.search(domain)
        field_to_match = []
        for record in available:
            field_to_match.append(record.field_ids.mapped("name"))
            for f in record.field_ids:
                if f.name in fields or f.field_id.name in fields:
                    result |= record
        _logger.info("FIELD TO MATCH: %s" % field_to_match)
        _logger.info("RESULT: %s" % result.ids)
        return result.ids, field_to_match


class SPPImportMatchFields(models.Model):
    _name = "spp.import.match.fields"
    _description = "Fields for Import Matching"

    name = fields.Char(compute="_compute_name")
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
        domain="[('model_id', '=', model_id)]",
        help="Fields to Match in Importing",
    )
    relation = fields.Char(related="field_id.relation")
    sub_field_id = fields.Many2one(
        "ir.model.fields",
        string="Sub-Field",
        ondelete="cascade",
        help="Sub Fields to Match in Importing",
    )
    match_id = fields.Many2one("spp.import.match", string="Match", ondelete="cascade")
    model_id = fields.Many2one(related="match_id.model_id")
    conditional = fields.Boolean()
    imported_value = fields.Char(help="This will be used as a condition to disregard this field if matched")

    def _compute_name(self):
        for rec in self:
            name = rec.field_id.name
            if rec.sub_field_id:
                name = rec.field_id.name + "/" + rec.sub_field_id.name
            rec.name = name

    @api.onchange("field_id")
    def _onchange_field_id(self):
        for rec in self:
            field_id = rec.field_id.id
            field_type = rec.field_id.ttype
            fields_list = []
            if field_type not in ("many2many", "one2many", "many2one"):
                for field in rec.match_id.field_ids:
                    new_id_str = str(field.id)
                    new_id_str_2 = "".join(letter for letter in new_id_str if letter.isalnum())
                    if "NewIdvirtual" not in new_id_str_2:
                        fields_list.append(field.field_id.id)

                duplicate_counter = 0
                for duplicate_field in fields_list:
                    if duplicate_field == field_id:
                        duplicate_counter += 1

                if duplicate_counter > 1:
                    raise ValidationError(_("Field '%s', already exists!") % rec.field_id.field_description)
