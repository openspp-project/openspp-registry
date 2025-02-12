import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomEditFarmer(models.Model):
    _inherit = "spp.change.request"  # Not merging classes as it might require significant refactoring.

    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    def _check_phone_exist(self):
        """
        Checks if phone is existing

        :raise UserError: Exception raised when applicant_phone is not existing.
        """
        request_type = self.request_type
        if "farm" not in request_type:
            if not self.applicant_phone:
                raise UserError(_("Phone No. is required."))

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.edit.farmer", "Edit Farmer")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestEditFarmer(models.Model):
    _name = "spp.change.request.edit.farmer"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Edit Farmer Change Request Type"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_edit_farmer.view_change_request_edit_farmer_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_edit_farmer.spp_dms_edit_farmer",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    FARMER_FIELDS = [
        "family_name",
        "given_name",
        "addl_name",
        "farmer_national_id",
        "gender",
        "marital_status",
        "birthdate",
        "farmer_household_size",
        "farmer_postal_address",
        "email",
        "formal_agricultural_training",
        "highest_education_level",
    ]

    def _get_dynamic_selection(self):
        options = self.env["gender.type"].search([])
        return [(option.value, option.code) for option in options]

    registrant_id = fields.Many2one(
        "res.partner",
        "Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )
    farmer_id = fields.Many2one(
        "res.partner",
        "Farmer",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # For ID Scanner Widget
    id_document_details = fields.Text("ID Document")

    # Member Details
    family_name = fields.Char()
    given_name = fields.Char()
    addl_name = fields.Char(string="Farmer Additional Name")
    farmer_national_id = fields.Char(string="National ID Number")
    mobile_tel = fields.Char(string="Mobile Telephone Number")
    gender = fields.Many2one("gender.type", "Sex")
    birthdate = fields.Date("Farmer Date of Birth")
    farmer_household_size = fields.Char()
    farmer_postal_address = fields.Char("Postal Address")
    email = fields.Char("E-mail Address")
    formal_agricultural_training = fields.Boolean()
    highest_education_level = fields.Selection(
        [
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("tertiary", "Tertiary"),
        ],
        string="Farmer Highest Educational Level",
    )
    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("widowed", "Widowed"),
            ("separated", "Separated"),
        ]
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_edit_farmer_rel",
        domain=[("request_type", "=", _name)],
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_edit_farmer_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_edit_farmer_id",
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

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        return

    def _get_default_change_request_id(self):
        """
        Get the default field name for change request id.
        """
        return "default_change_request_edit_farmer_id"

    def validate_data(self):
        validate_data = super().validate_data()
        error_message = []
        if not self.farmer_id:
            error_message.append(_("The Farmer is required!"))
        if error_message:
            raise ValidationError("\n".join(error_message))

        return validate_data

    def update_live_data(self):
        self.ensure_one()

        # Edit the Farmer (res.partner)
        farmer_vals = {}
        for farmer_field in self.FARMER_FIELDS:
            if self[farmer_field]:
                farmer_vals[farmer_field] = self[farmer_field]
        self.farmer_id.write(farmer_vals)
        if self.mobile_tel:
            self.insert_phone_number(self.farmer_id.id, self.mobile_tel)

        if self.farmer_national_id:
            self.insert_id(self.farmer_id.id, self.farmer_national_id)

        self.farmer_id.name_change()

        return self.farmer_id

    def insert_phone_number(self, individual_id, mobile_no):
        if mobile_no:
            current_phone = self.env["g2p.phone.number"].search([("partner_id", "=", individual_id)], limit=1)
            if not current_phone:
                individual_phone_vals = {"partner_id": individual_id, "phone_no": mobile_no}
                self.env["g2p.phone.number"].create(individual_phone_vals)
            else:
                current_phone.write({"phone_no": mobile_no})

    def insert_id(self, individual_id, national_id):
        if national_id:
            current_id = self.env["g2p.reg.id"].search(
                [
                    ("partner_id", "=", individual_id),
                    ("value", "=", national_id),
                    (
                        "id_type",
                        "=",
                        self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                    ),
                ]
            )
            if not current_id:
                existing_national_id = self.env["g2p.reg.id"].search(
                    [
                        ("partner_id", "=", individual_id),
                        (
                            "id_type",
                            "=",
                            self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                        ),
                    ]
                )
                id_vals = {
                    "partner_id": individual_id,
                    "value": national_id,
                    "id_type": self.env.ref("spp_farmer_registry_base.id_type_national_id").id,
                }
                if existing_national_id:
                    existing_national_id.write(id_vals)
                else:
                    self.env["g2p.reg.id"].create(id_vals)

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
