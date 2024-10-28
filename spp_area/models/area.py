# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import textwrap

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPArea(models.Model):
    """
    Represents an area in the OpenSPP system.

    This model defines the structure and behavior of geographical areas,
    including their hierarchical relationships, names, codes, and other attributes.
    """

    _name = "spp.area"
    _description = "Area"
    _order = "id desc"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "parent_id,name"

    parent_id = fields.Many2one("spp.area", "Parent")
    complete_name = fields.Char(compute="_compute_complete_name", recursive=True, translate=True)
    name = fields.Char(translate=True, compute="_compute_name", store=True)
    draft_name = fields.Char(required=True, translate=True)
    parent_path = fields.Char(index=True)
    code = fields.Char()
    altnames = fields.Char("Alternate Name")
    level = fields.Integer(help="This is the area level for importing")
    area_level = fields.Integer(compute="_compute_area_level", help="This is the main area level")
    child_ids = fields.One2many("spp.area", "id", "Child", compute="_compute_get_childs")
    kind = fields.Many2one("spp.area.kind")
    area_sqkm = fields.Float("Area (sq/km)")

    _sql_constraints = [
        (
            "code_unique",
            "unique (code)",
            "Code is already exists!",
        )
    ]

    @api.depends("draft_name", "code")
    def _compute_name(self):
        """
        Compute the name for the area to include the code.

        The name is set as a combination of the code (if present) and the draft name.
        """
        for rec in self:
            name = rec.draft_name or ""

            if rec.code:
                name = f"{rec.code} - {name}"

            rec.name = name

    def _compute_get_childs(self):
        """
        Compute the child areas of the current area.

        This method searches for all areas that have the current area as their parent
        and assigns them to the child_ids field.
        """
        for rec in self:
            child_ids = self.env["spp.area"].search([("parent_id", "=", rec.id)])
            rec.child_ids = child_ids

    @api.depends("parent_id")
    def _compute_area_level(self):
        """
        Compute the area level based on the parent area.

        If the area has a parent, its level is set to the parent's level plus one.
        If it doesn't have a parent, its level is set to 0.
        """
        for rec in self:
            if rec.parent_id:
                rec.area_level = rec.parent_id.area_level + 1
            else:
                rec.area_level = 0

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """
        Validate the area level when the parent area changes.

        Raises a ValidationError if the resulting area level would exceed 10.
        """
        for rec in self:
            if rec.area_level > 10:
                raise ValidationError(
                    _(
                        textwrap.fill(
                            textwrap.dedent(
                                """Max level exceeded! Can't have area with level greater
                        than 10 and your current area is level %s."""
                                % rec.area_level
                            )
                        )
                    )
                )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        """
        Compute the complete name of the area.

        The complete name includes the parent's complete name (if any) and the area's own name.
        """
        for rec in self:
            if rec.id:
                if rec.parent_id:
                    rec.complete_name = f"{rec.parent_id.complete_name} > {rec.name}"
                else:
                    rec.complete_name = rec.name
            else:
                rec.complete_name = None

    @api.model
    def create(self, vals):
        """
        Create a new area record.

        This method overrides the default create method to add additional validation
        and translation handling.

        :param vals: The values for the new record.
        :return: The newly created area record.
        :raises ValidationError: If an area with the same name and code already exists.
        """
        area_name = self.name
        if "name" in vals:
            area_name = vals["name"]
        area_code = self.code
        if "code" in vals:
            area_code = vals["code"]
        curr_area = self.env["spp.area"].search(
            [
                ("name", "=", area_name),
                ("code", "=", area_code),
            ]
        )

        if curr_area:
            raise ValidationError(_("Area already exist!"))
        else:
            Area = super().create(vals)
            Languages = self.env["res.lang"].search([("active", "=", True)])
            vals_list = []
            for lang_code in Languages:
                vals_list.append(
                    {
                        "name": "spp.area,draft_name",
                        "lang": lang_code.code,
                        "res_id": Area.id,
                        "src": Area.draft_name,
                        "value": None,
                        "state": "to_translate",
                        "type": "model",
                    }
                )

            return Area

    def write(self, vals):
        """
        Update an existing area record.

        This method overrides the default write method to add additional validation.

        :param vals: The values to update.
        :return: The result of the write operation.
        :raises ValidationError: If an area with the same name and code already exists.
        """
        for rec in self:
            area_name = rec.name
            if "name" in vals:
                area_name = vals["name"]
            area_code = rec.code
            if "code" in vals:
                area_code = vals["code"]
            curr_area = self.env["spp.area"].search(
                [
                    ("name", "=", area_name),
                    ("code", "=", area_code),
                    ("id", "!=", rec.id),
                ]
            )
            if curr_area:
                raise ValidationError(_("Area already exist!"))
            else:
                return super().write(vals)

    def open_area_form(self):
        """
        Open the form view of the area.

        :return: A dictionary containing the action to open the area form view.
        """
        for rec in self:
            return {
                "name": "Area",
                "view_mode": "form",
                "res_model": "spp.area",
                "res_id": rec.id,
                "view_id": self.env.ref("spp_area.view_spparea_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "flags": {"mode": "readonly"},
            }


class OpenSPPAreaKind(models.Model):
    """
    Represents the type or kind of an area in the OpenSPP system.

    This model defines the structure and behavior of area types, including
    their hierarchical relationships and names.
    """

    _name = "spp.area.kind"
    _description = "Area Type"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "parent_id,name"

    parent_id = fields.Many2one("spp.area.kind", "Parent")
    parent_path = fields.Char(index=True)
    name = fields.Char(required=True)
    complete_name = fields.Char(compute="_compute_complete_name", recursive=True, translate=True)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        """
        Compute the complete name of the area type.

        The complete name includes the parent's complete name (if any) and the area type's own name.
        """
        for rec in self:
            if rec.id:
                if rec.parent_id:
                    rec.complete_name = f"{rec.parent_id.complete_name} > {rec.name}"
                else:
                    rec.complete_name = rec.name
            else:
                rec.complete_name = None

    def unlink(self):
        """
        Delete an area type record.

        This method overrides the default unlink method to add additional validation.
        It prevents the deletion of default area types and area types that are in use.

        :raises ValidationError: If trying to delete a default area type or an area type in use.
        """
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "spp.area.kind")]
            )
            if external_identifier and external_identifier.name:
                raise ValidationError(_("Can't delete default Area Type"))
            else:
                areas = self.env["spp.area"].search([("kind", "=", rec.id)])
                if areas:
                    raise ValidationError(_("Can't delete used Area Type"))
                else:
                    return super().unlink()

    def write(self, vals):
        """
        Update an existing area type record.

        This method overrides the default write method to prevent editing of default area types.

        :param vals: The values to update.
        :return: The result of the write operation.
        """
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "spp.area.kind")]
            )
            if external_identifier and external_identifier.name:
                vals = {}
            return super().write(vals)
