import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)

# Shared Constants
PARTNER_MODEL = "res.partner"
CREATE_FARM_MODEL = "spp.change.request.create.farm"
FARM_ACTIVITY_MODEL = "spp.farm.activity"
FARM_ASSET_MODEL = "spp.farm.asset"
REGISTRANT_DOMAIN = [("is_registrant", "=", True), ("is_group", "=", True)]


class ChangeRequestTypeCustomCreateFarm(models.Model):
    _inherit = "spp.change.request"  # Not merging classes as it might require significant refactoring.

    registrant_id = fields.Many2one(
        PARTNER_MODEL,
        "Registrant",
        domain=REGISTRANT_DOMAIN,
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
        new_request_type = ("spp.change.request.create.farm", "Create Farm")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestCreateFarm(models.Model):
    _name = CREATE_FARM_MODEL
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Change Request Create Farm"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_create_farm.view_change_request_create_farm_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_create_farm.spp_dms_create_farm",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    def _get_dynamic_selection(self):
        options = self.env["gender.type"].search([])
        return [(option.value, option.code) for option in options]

    registrant_id = fields.Many2one(
        PARTNER_MODEL,
        "Add to Group",
        domain=REGISTRANT_DOMAIN,
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # For ID Scanner Widget
    id_document_details = fields.Text("ID Document")

    # Group Details
    group_name = fields.Char("Group Name")
    group_kind = fields.Many2one(
        "g2p.group.kind",
        string="Group Kind",
        default=lambda self: self.env.ref("spp_farmer_registry_base.kind_farm", raise_if_not_found=False),
    )
    farm_crop_act_ids = fields.One2many(FARM_ACTIVITY_MODEL, "crop_cr_farm_id", string="Crop Agricultural Activities")
    farm_live_act_ids = fields.One2many(
        FARM_ACTIVITY_MODEL, "live_cr_farm_id", string="Livestock Agricultural Activities"
    )
    farm_aqua_act_ids = fields.One2many(
        FARM_ACTIVITY_MODEL,
        "aqua_cr_farm_id",
        string="Aquaculture Agricultural Activities",
    )
    farm_asset_ids = fields.One2many(FARM_ASSET_MODEL, "asset_cr_farm_id", string="Farm Assets")
    farm_machinery_ids = fields.One2many(FARM_ASSET_MODEL, "machinery_cr_farm_id", string="Farm Machinery")

    # Member Details
    farmer_family_name = fields.Char()
    farmer_given_name = fields.Char()
    farmer_addtnl_name = fields.Char(string="Farmer Additional Name")
    farmer_national_id = fields.Char(string="National ID Number")
    farmer_mobile_tel = fields.Char(string="Mobile Telephone Number")
    farmer_sex = fields.Many2one("gender.type", "Sex")
    farmer_birthdate = fields.Date("Farmer Date of Birth")
    farmer_household_size = fields.Char()
    farmer_postal_address = fields.Char("Postal Address")
    farmer_email = fields.Char("E-mail Address")
    farmer_formal_agricultural = fields.Boolean()
    farmer_highest_education_level = fields.Selection(
        [
            ("none", "None"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("tertiary", "Tertiary"),
        ],
        string="Farmer Highest Educational Level",
    )
    farmer_marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("widowed", "Widowed"),
            ("separated", "Separated"),
        ]
    )

    # Land Record
    land_name = fields.Char(string="Parcel Name/ID")
    land_acreage = fields.Float()
    land_coordinates = fields.GeoPointField()
    land_geo_polygon = fields.GeoPolygonField(string="Land Polygons")

    # Farm Details
    details_legal_status = fields.Selection(
        [
            ("self", "Owned by self"),
            ("family", "Owned by family"),
            ("extended community", "Owned by extended community"),
            ("cooperative", "Owned by cooperative"),
            ("government", "Owned by Government"),
            ("leased", "Leased from actual owner"),
            ("unknown", "Do not Know"),
        ],
        string="Legal Status",
    )

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
        """
        Handles changes to the registrant_id field.
        Currently returns without performing any actions.
        """
        return

    @api.onchange("farmer_birthdate")
    def _onchange_farmer_birthdate(self):
        """
        Validates that the farmer's birthdate is not in the future.

        :raise ValidationError: If birthdate is later than today's date.
        """
        if self.farmer_birthdate and self.farmer_birthdate > fields.date.today():
            raise ValidationError(_("Birthdate should not be on a later date."))

    @api.constrains("farmer_mobile_tel")
    def _check_farmer_mobile_tel(self):
        """
        Validates the farmer's mobile telephone number format based on country code.
        Uses phone validation to check if number matches country format.

        :raise ValidationError: If phone number format is incorrect.
        """
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
                phone_validation.phone_parse(rec.farmer_mobile_tel, country_code)
            except UserError as e:
                raise ValidationError(_("Incorrect phone number format")) from e

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        """
        Handles changes to the id_document_details field.
        Currently returns without performing any actions.
        """
        return

    def _get_default_change_request_id(self):
        """
        Gets the default field name for change request id.

        :return: String containing the default field name
        :rtype: str
        """
        return "default_change_request_create_farm_id"

    def validate_data(self):
        """
        Validates the required fields for creating a farm change request.
        Checks for mandatory fields like group name, group kind, and farmer details.

        :return: Result from parent class validate_data
        :raise ValidationError: If any required fields are missing
        """
        validate_data = super().validate_data()
        error_message = []
        if not self.group_name:
            error_message.append(_("The Group Name is required!"))
        if not self.group_kind:
            error_message.append(_("The Group Kind is required!"))
        if self.group_kind and self.group_kind.id == self.env.ref("spp_farmer_registry_base.kind_farm").id:
            if not self.farmer_family_name:
                error_message.append(_("The Family Name is required!"))
            if not self.farmer_given_name:
                error_message.append(_("The Given Name is required!"))

        if error_message:
            raise ValidationError("\n".join(error_message))

        return validate_data

    def update_live_data(self):
        """
        Creates a new group (res.partner) record with farm details and updates related records.

        This method:
        1. Creates a new group with farmer and land details
        2. Links agricultural activities to the new group
        3. Links farm assets and machinery to the new group
        4. Updates the change request record

        :return: The newly created group record
        :rtype: res.partner
        """
        self.ensure_one()

        # Create the group (res.partner)

        group_vals = {
            "name": self.group_name,
            "is_registrant": True,
            "is_group": True,
            "farmer_family_name": self.farmer_family_name or None,
            "farmer_given_name": self.farmer_given_name or None,
            "farmer_addtnl_name": self.farmer_addtnl_name or None,
            "farmer_national_id": self.farmer_national_id or None,
            "farmer_mobile_tel": self.farmer_mobile_tel or None,
            "farmer_sex": self.farmer_sex.id if self.farmer_sex else None,
            "farmer_birthdate": self.farmer_birthdate or None,
            "farmer_household_size": self.farmer_household_size or None,
            "farmer_postal_address": self.farmer_postal_address or None,
            "farmer_email": self.farmer_email or None,
            "farmer_formal_agricultural": self.farmer_formal_agricultural or False,
            "farmer_highest_education_level": self.farmer_highest_education_level or None,
            "farmer_marital_status": self.farmer_marital_status or None,
            "land_name": self.land_name or None,
            "land_acreage": self.land_acreage or None,
            "land_coordinates": self.land_coordinates or None,
            "land_geo_polygon": self.land_geo_polygon or None,
            "details_legal_status": self.details_legal_status or None,
        }
        if self.group_kind:
            group_vals["kind"] = self.group_kind.id
        group = self.env["res.partner"].create(group_vals)

        if self.farm_crop_act_ids:
            for act in self.farm_crop_act_ids:
                act.crop_farm_id = group.id
        if self.farm_live_act_ids:
            for act in self.farm_live_act_ids:
                act.live_farm_id = group.id
        if self.farm_aqua_act_ids:
            for act in self.farm_aqua_act_ids:
                act.aqua_farm_id = group.id
        if self.farm_asset_ids:
            for asset in self.farm_asset_ids:
                asset.asset_farm_id = group.id
        if self.farm_machinery_ids:
            for machinery in self.farm_machinery_ids:
                machinery.machinery_farm_id = group.id

        cr_vals = {
            "applicant_phone": self.farmer_mobile_tel or None,
            "registrant_id": group.id,
        }
        if group.group_membership_ids:
            cr_vals["applicant_id"] = group.group_membership_ids[0].individual.id

        self.change_request_id.write(cr_vals)

        return group

    def open_registrant_details_form(self):
        """
        Opens a form view showing the registrant's details in readonly mode.

        :return: Action dictionary for opening the form view
        :rtype: dict
        """
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


class ChangeRequestCreateFarmAgriculturalActivity(models.Model):
    _inherit = FARM_ACTIVITY_MODEL

    crop_cr_farm_id = fields.Many2one(CREATE_FARM_MODEL, string="Crop Farm")
    live_cr_farm_id = fields.Many2one(CREATE_FARM_MODEL, string="Livestock Farm")
    aqua_cr_farm_id = fields.Many2one(CREATE_FARM_MODEL, string="Aqua Farm")


class ChangeRequestCreateFarmAssets(models.Model):
    _inherit = FARM_ASSET_MODEL

    asset_cr_farm_id = fields.Many2one(CREATE_FARM_MODEL, string="Asset Farm")
    machinery_cr_farm_id = fields.Many2one(CREATE_FARM_MODEL, string="Machinery Farm")
