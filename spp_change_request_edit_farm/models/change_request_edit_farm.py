import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomEditFarm(models.Model):
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
        new_request_type = ("spp.change.request.edit.farm", "Edit Farm")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestEditFarm(models.Model):
    _name = "spp.change.request.edit.farm"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Edit Farm Change Request Type"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_edit_farm.view_change_request_edit_farm_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_edit_farm.spp_dms_edit_farm",
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
    group_kind = fields.Many2one(
        "g2p.group.kind",
        string="Group Kind",
        default=lambda self: self.env.ref("spp_farmer_registry_base.kind_farm", raise_if_not_found=False),
    )
    farm_crop_act_ids = fields.One2many("spp.farm.activity", "crop_cr_farm_id", string="Crop Agricultural Activities")
    farm_live_act_ids = fields.One2many(
        "spp.farm.activity", "live_cr_farm_id", string="Livestock Agricultural Activities"
    )
    farm_aqua_act_ids = fields.One2many(
        "spp.farm.activity",
        "aqua_cr_farm_id",
        string="Aquaculture Agricultural Activities",
    )
    farm_asset_ids = fields.One2many("spp.farm.asset", "asset_cr_farm_id", string="Farm Assets")
    farm_machinery_ids = fields.One2many("spp.farm.asset", "machinery_cr_farm_id", string="Farm Machinery")

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
        relation="spp_change_request_edit_farm_rel",
        domain=[("request_type", "=", _name)],
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_edit_farm_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_edit_farm_id",
        string="DMS Files",
        auto_join=True,
    )

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        return

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
        return "default_change_request_edit_farm_id"

    def validate_data(self):
        super().validate_data()
        error_message = []
        if not self.registrant_id:
            error_message.append(_("The Group or Farm is required!"))
        if error_message:
            raise ValidationError("\n".join(error_message))

        return

    FARM_FIELDS = [
        "group_name",
        "group_kind",
        "land_name",
        "land_acreage",
        "land_coordinates",
        "land_geo_polygon",
        "details_legal_status",
    ]

    RES_PARTNER_FIELDS = [
        "name",
        "kind",
        "land_name",
        "land_acreage",
        "land_coordinates",
        "land_geo_polygon",
        "details_legal_status",
    ]

    def update_live_data(self):
        self.ensure_one()

        # Update the group (res.partner)

        group_vals = {
            "is_registrant": True,
            "is_group": True,
        }
        for farm_field, res_partner_field in zip(self.FARM_FIELDS, self.RES_PARTNER_FIELDS, strict=True):
            if self[farm_field]:
                group_vals[res_partner_field] = self[farm_field]

        group = self.registrant_id
        group.write(group_vals)

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
            "registrant_id": group.id,
        }
        if group.group_membership_ids:
            cr_vals["applicant_id"] = group.group_membership_ids[0].individual.id

        self.change_request_id.write(cr_vals)

        return group

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


class ChangeRequestEditFarmAgriculturalActivity(models.Model):
    _inherit = "spp.farm.activity"

    crop_cr_farm_id = fields.Many2one("spp.change.request.edit.farm", string="Crop Farm")
    live_cr_farm_id = fields.Many2one("spp.change.request.edit.farm", string="Livestock Farm")
    aqua_cr_farm_id = fields.Many2one("spp.change.request.edit.farm", string="Aqua Farm")


class ChangeRequestEditFarmAssets(models.Model):
    _inherit = "spp.farm.asset"

    asset_cr_farm_id = fields.Many2one("spp.change.request.edit.farm", string="Asset Farm")
    machinery_cr_farm_id = fields.Many2one("spp.change.request.edit.farm", string="Machinery Farm")
