import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomCreateFarm(models.Model):
    _inherit = "spp.change.request"  # Not merging classes as it might require significant refactoring.

    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.create.farm", "Create Farm")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestCreateFarm(models.Model):
    _name = "spp.change.request.create.farm"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Create Farm Change Request Type"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_create_farm.view_change_request_create_farm_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_create_farm.spp_dms_create_farm",
        # "spp_change_request.spp_dms_birth_certificate",
        # "spp_change_request.spp_dms_applicant_spp_card",
        # "spp_change_request.spp_dms_applicant_uid_card",
        # "spp_change_request.spp_dms_custody_certificate",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    def _get_dynamic_selection(self):
        options = self.env["gender.type"].search([])
        return [(option.value, option.code) for option in options]

    registrant_id = fields.Many2one(
        "res.partner",
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # For ID Scanner Widget
    id_document_details = fields.Text("ID Document")

    # Group Details
    group_name = fields.Char("Group Name")
    group_kind = fields.Many2one("g2p.group.kind", string="Group Kind")

    # Member Details
    full_name = fields.Char(compute="_compute_full_name", readonly=True)
    family_name = fields.Char()
    given_name = fields.Char()
    additional_name = fields.Char()
    mobile_tel = fields.Char()
    sex = fields.Many2one("gender.type")
    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("widowed", "Widowed"),
            ("married", "Married"),
            ("separated", "Separated"),
        ],
    )
    birth_place = fields.Char()
    birthdate = fields.Date()
    birthdate_not_exact = fields.Boolean()
    email = fields.Char()
    national_id_number = fields.Char("National ID Number")

    membership_kind = fields.Many2one("g2p.group.membership.kind")

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_create_farm_rel",
        domain=[("request_type", "=", _name)],
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_create_farm_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_create_farm_id",
        string="DMS Files",
        auto_join=True,
    )

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        return

    @api.onchange("birthdate")
    def _onchange_birthdate(self):
        if self.birthdate and self.birthdate > fields.date.today():
            raise ValidationError(_("Birthdate should not be on a later date."))

    @api.constrains("mobile_tel")
    def _check_mobile_tel(self):
        for rec in self:
            cr = rec.change_request_id
            country_code = (
                cr.registrant_id.country_id.code
                if cr.registrant_id and cr.registrant_id.country_id and cr.registrant_id.country_id.code
                else None
            )
            if country_code is None:
                country_code = (
                    cr.company_id.country_id.code
                    if cr.company_id.country_id and cr.company_id.country_id.code
                    else None
                )
            try:
                phone_validation.phone_parse(rec.mobile_tel, country_code)
            except UserError as e:
                raise ValidationError(_("Incorrect phone number format")) from e

    @api.depends("given_name", "additional_name", "family_name")
    def _compute_full_name(self):
        for rec in self:
            full_name = f"{rec.family_name or ''}, {rec.given_name or ''}" f" {rec.additional_name or ''}"
            rec.full_name = full_name.title()

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        return
        # TODO: Implement this method
        # if self.dms_directory_ids:
        #     if self.id_document_details:
        #         try:
        #             details = json.loads(self.id_document_details)
        #         except json.decoder.JSONDecodeError as e:
        #             details = None
        #             _logger.error(e)
        #         if details:
        #             # Upload to DMS
        #             if details["image"]:
        #                 if self._origin:
        #                     directory_id = self._origin.dms_directory_ids[0].id
        #                 else:
        #                     directory_id = self.dms_directory_ids[0].id
        #                 dms_vals = {
        #                     "name": "UID_" + details["document_number"] + ".jpg",
        #                     "directory_id": directory_id,
        #                     "category_id": self.env.ref("spp_change_request.spp_dms_uid_card").id,
        #                     "content": details["image"],
        #                 }
        #                 # TODO: Should be added to vals["dms_file_ids"] but it is
        #                 # not writing to one2many field using Command.create()
        #                 self.env["spp.dms.file"].create(dms_vals)
        #
        #             # TODO: grand_father_name and father_name
        #             vals = {
        #                 "family_name": details["family_name"],
        #                 "given_name": details["given_name"],
        #                 "birthdate": details["birth_date"],
        #                 "gender": details["gender"],
        #                 "id_document_details": "",
        #                 "birth_place": details["birth_place_city"],
        #                 # TODO: Fix not writing to one2many field: dms_file_ids
        #                 # "dms_file_ids": [(Command.create(dms_vals))],
        #             }
        #             self.update(vals)
        # else:
        #     raise UserError(_("There are no directories defined for this change request."))

    def _get_default_change_request_id(self):
        """
        Get the default field name for change request id.
        """
        return "default_change_request_create_group_id"

    def validate_data(self):
        super().validate_data()
        error_message = []
        if not self.group_name:
            error_message.append(_("The Group Name is required!"))
        if not self.group_kind:
            error_message.append(_("The Group Kind is required!"))

        if error_message:
            raise ValidationError("\n".join(error_message))

        return

    def update_live_data(self):
        self.ensure_one()
        individual = None

        if self.family_name or self.given_name:
            # Create a new individual (res.partner)

            individual_vals = {
                "name": self.full_name,
                "family_name": self.family_name,
                "given_name": self.given_name,
                "addl_name": self.additional_name,
                "phone": self.mobile_tel,
                "gender": self.sex.id,
                "birth_place": self.birth_place,
                "birthdate": self.birthdate,
                "birthdate_not_exact": self.birthdate_not_exact,
                "email": self.email,
                "is_registrant": True,
                "is_group": False,
            }
            phone = [(Command.create({"phone_no": self.mobile_tel}))] if self.mobile_tel else []
            if phone:
                individual_vals["phone_number_ids"] = phone

            reg_ids = (
                [
                    (
                        Command.create(
                            {
                                "id_type": self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                                "value": self.national_id_number,
                            }
                        )
                    )
                ]
                if self.national_id_number
                else []
            )
            if reg_ids:
                individual_vals["reg_ids"] = reg_ids

            individual = self.env["res.partner"].create(individual_vals)

        # Create the group (res.partner)

        group_vals = {
            "name": self.group_name,
            "is_registrant": True,
            "is_group": True,
        }
        if self.group_kind:
            group_vals["kind"] = self.group_kind.id
        group = self.env["res.partner"].create(group_vals)

        # Add membership if individual is created
        if individual:
            vals_membership = {
                "group": group.id,
                "individual": individual.id,
            }
            if self.membership_kind:
                memberships_kind = [Command.link(self.membership_kind.id)]
                vals_membership["kind"] = memberships_kind

            self.env["g2p.group.membership"].create(vals_membership)

    def open_registrant_details_form(self):
        self.ensure_one()
        res_id = self.registrant_id.id
        form_id = self.env.ref("g2p_registry_group.view_groups_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
            "hide_from_cr": 1,
        }
        action.update(
            {
                "name": _("Group Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
