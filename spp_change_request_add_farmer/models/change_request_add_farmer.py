import json
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Constants for model names
MODEL_ADD_FARMER = "spp.change.request.add.farmer"
MODEL_PARTNER = "res.partner"


class ChangeRequestTypeCustomAddFarmer(models.Model):
    _inherit = "spp.change.request"  # Not merging classes as it might require significant refactoring.

    registrant_id = fields.Many2one(
        MODEL_PARTNER,
        "Registrant",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    def _check_phone_exist(self):
        """
        Checks if phone is existing

        :raise UserError: Exception raised when applicant_phone is not existing.
        """
        request_type = self.request_type
        if "farm" not in request_type and not self.applicant_phone:
            raise UserError(_("Phone No. is required."))

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = (MODEL_ADD_FARMER, "Add Farmer")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestAddChildren(models.Model):
    _name = MODEL_ADD_FARMER
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Add Farmer Change Request Type"
    _order = "id desc"

    # Initialize CR constants
    VALIDATION_FORM = "spp_change_request_add_farmer.view_change_request_add_farmer_validation_form"
    REQUIRED_DOCUMENT_TYPE = [
        "spp_change_request_add_farmer.spp_dms_add_farmer",
    ]

    # Mandatory initialize source and destination center areas
    # If validators will be allowed for both, make the values the same
    SRC_AREA_FLD = ["registrant_id", "area_center_id"]
    DST_AREA_FLD = SRC_AREA_FLD

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        MODEL_PARTNER,
        "Add to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # For ID Scanner Widget
    id_document_details = fields.Text("ID Document")

    # Target Group Fields
    group_member_ids = fields.One2many("spp.change.request.group.members", "group_add_farmer_id", "Group Members")

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_add_farmer_rel",
        domain=[("request_type", "=", _name)],
    )

    # DMS Field
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_add_farmer_id",
        string="DMS Directories",
        auto_join=True,
    )
    dms_file_ids = fields.One2many(
        "spp.dms.file",
        "change_request_add_farmer_id",
        string="DMS Files",
        auto_join=True,
    )

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        """
        Handles changes to the registrant_id field.
        Clears group members when registrant changes and updates the change request's registrant.

        Returns:
            None
        """
        if self.group_member_ids:
            self.group_member_ids = [(Command.clear())]
        self.change_request_id.registrant_id = self.registrant_id.id

    @api.onchange("id_document_details")
    def _onchange_scan_id_document_details(self):
        """
        Processes scanned ID document details.
        Creates DMS file entries and updates individual details based on scanned information.

        Raises:
            UserError: If no directories are defined for the change request.

        Returns:
            None
        """
        if self.dms_directory_ids:
            if self.id_document_details:
                try:
                    details = json.loads(self.id_document_details)
                except json.decoder.JSONDecodeError as e:
                    details = None
                    _logger.error(e)
                if details:
                    # Upload to DMS
                    if details["image"]:
                        if self._origin:
                            directory_id = self._origin.dms_directory_ids[0].id
                        else:
                            directory_id = self.dms_directory_ids[0].id
                        dms_vals = {
                            "name": "UID_" + details["document_number"] + ".jpg",
                            "directory_id": directory_id,
                            "category_id": self.env.ref("spp_change_request.spp_dms_uid_card").id,
                            "content": details["image"],
                        }
                        # TODO: Should be added to vals["dms_file_ids"] but it is
                        # not writing to one2many field using Command.create()
                        self.env["spp.dms.file"].create(dms_vals)

                    # TODO: grand_father_name and father_name
                    vals = {
                        "family_name": details["family_name"],
                        "given_name": details["given_name"],
                        "birthdate": details["birth_date"],
                        "gender": details["gender"],
                        "id_document_details": "",
                        "birth_place": details["birth_place_city"],
                        # TODO: Fix not writing to one2many field: dms_file_ids
                        # "dms_file_ids": [(Command.create(dms_vals))],
                    }
                    self.update(vals)
        else:
            raise UserError(_("There are no directories defined for this change request."))

    def _get_default_change_request_id(self):
        """
        Returns the default field name for change request id.

        Returns:
            str: The default field name 'default_change_request_add_farmer_id'
        """
        return "default_change_request_add_farmer_id"

    def validate_data(self):
        """
        Validates the change request data.
        Ensures at least one farmer is added to the group.

        Raises:
            ValidationError: If validation fails (no farmers added)

        Returns:
            bool: True if validation passes
        """
        validate_data = super().validate_data()
        error_message = []
        if not self.group_member_ids:
            error_message.append(_("Need to add at least one farmer!"))

        if error_message:
            raise ValidationError("\n".join(error_message))

        return validate_data

    def update_live_data(self):
        """
        Updates the live data by creating group memberships for added farmers.
        Creates membership records linking individuals to the group with specified roles and start dates.

        Returns:
            None
        """
        self.ensure_one()

        for group_member in self.group_member_ids:
            self.env["g2p.group.membership"].create(
                {
                    "group": self.registrant_id.id,
                    "individual": group_member.individual_id.id,
                    "kind": group_member.kind_ids.ids,
                    "start_date": group_member.start_date,
                }
            )

    def open_registrant_details_form(self):
        """
        Opens a form view showing the registrant's details in readonly mode.

        Returns:
            dict: Action dictionary for opening the form view
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
