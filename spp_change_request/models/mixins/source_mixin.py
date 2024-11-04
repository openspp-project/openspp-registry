# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestSourceMixin(models.AbstractModel):
    """
    Change Request Data Source mixin.
    ---------------------------------
    This mixin is inherited by objects implementing a change Request.

    Example:

    .. code-block:: python

        class ChangeRequestAddChildren(models.Model):
            _name = "spp.change.request.demo.add.children"
            _inherit = [
                "spp.change.request.source.mixin",
                "spp.change.request.validation.sequence.mixin",
            ]
            _description = "Add Children Change Request Type"

            # Initialize DMS Storage
            DMS_STORAGE = "spp_change_request_add_children.attachment_storage_add_children"
            VALIDATION_FORM = "spp_change_request_add_children.view_change_request_add_children_validation_form"
            REQUIRED_DOCUMENT_TYPE = [
                "change_request.dms_birth_certificate_category",
            ]

    """

    _name = "spp.change.request.source.mixin"
    _description = "Change Request Data Source Mixin"
    _rec_name = "change_request_id"

    REQUIRED_DOCUMENT_TYPE = []  # List of required document category `spp.dms.category`
    VALIDATION_FORM = None
    AUTO_APPLY_CHANGES = True

    registrant_id = fields.Many2one("res.partner", "Registrant", domain=[("is_registrant", "=", True)])
    applicant_id = fields.Many2one(
        "res.partner",
        "Applicant",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    applicant_phone = fields.Char("Applicant's Phone Number", related="change_request_id.applicant_phone")
    change_request_id = fields.Many2one("spp.change.request", "Change Request", required=True)
    assign_to_id = fields.Many2one("res.users", "Assigned to", related="change_request_id.assign_to_id")
    last_validated_by_id = fields.Many2one(
        "res.users", "Last Validator", related="change_request_id.last_validated_by_id"
    )
    date_validated = fields.Datetime(related="change_request_id.date_validated")
    state = fields.Selection(
        related="change_request_id.state",
        string="Status",
        readonly=True,
    )

    # Target Fields
    group_address = fields.Text(related="registrant_id.address", readonly=True)
    group_registration_date = fields.Date(related="registrant_id.registration_date", readonly=True)

    # DMS Field
    # dms_directory_ids = fields.One2many(
    #    "spp.dms.directory",
    #    "change_request_id",
    #    string="DMS Directories",
    #    auto_join=True,
    # )
    # dms_file_ids = fields.One2many(
    #    "spp.dms.file",
    #    "change_request_id",
    #    string="DMS Files",
    #    auto_join=True,
    # )

    current_user_assigned = fields.Boolean(compute="_compute_current_user_assigned", default=False)

    def _update_registrant_id(self, res):
        for rec in res:
            if rec.registrant_id:
                rec.change_request_id.update({"registrant_id": rec.registrant_id.id})

    def get_request_type_view_id(self):
        """
        Retrieve form view ID.

        :return: form view ID
        :rtype: int
        """
        return self.env["ir.ui.view"].sudo().search([("model", "=", self._name), ("type", "=", "form")], limit=1).id

    def update_live_data(self):
        """
        This method is meant to be overridden by the child classes to update the data of the registrant.

        """
        raise NotImplementedError()

    def validate_data(self):
        """
        This method is meant to be overridden by the child classes to validate the data of the change request
        before submitting for review.

        :raise ValidationError: Exception raised when something is not valid.
        """
        self.ensure_one()
        self.check_required_documents()

    def action_submit(self):
        """
        This method is called when the Change Request is requested for validation by a user.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_submit"
                type="object"
            />

        :raise ValidationError: Exception raised when something is not valid.
        """
        for rec in self:
            rec._on_submit(rec.change_request_id)

    def _on_submit(self, request):
        """
        This method is called when the Change Request is submitted for validation.

        :param request: The request.
        :raise UserError: Exception raised when something is not valid.
        """
        self.ensure_one()
        if request.state == "draft":
            # Validate the submitted data
            self.validate_data()
            # Mark previous activity as 'done'
            request.last_activity_id.action_done()
            # Create validation activity
            activity_type = "spp_change_request.validation_activity"
            summary = _("For Validation")
            note = _(
                "The change request is now set for validation. Depending on the "
                "validation sequence, this may be subjected to one or more validations."
            )
            request._generate_activity(activity_type, summary, note)

            # Update change request
            request.update(
                {
                    "date_requested": fields.Datetime.now(),
                    "state": "pending",
                    "assign_to_id": None,
                    "rejected_by_id": None,
                    "date_rejected": None,
                    "rejected_remarks": None,
                }
            )
        else:
            # TODO: @edwin Should we use UserError or ValidationError?
            raise UserError(_("The request must be in draft state to be set to pending validation."))

    def action_validate(self):
        """
        This method is called when the Change Request is validated by a user.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_validate"
                type="object"
            />

        :raise ValidationError: Exception raised when something is not valid.
        """
        for rec in self:
            return rec._on_validate(rec.change_request_id)

    def auto_apply_conditions(self):
        """
        Check if conditions/requirements are met:
        if requirements are met, auto apply will execute
        else it will not execute

        NOTE: Overwrite this method on the inherited models if conditions/requirements are
              needed to check before executing auto apply.

              Return True if requirements are met
              else False
        """
        return True

    def _on_validate(self, request):
        """
        This method is called when the Change Request is validated by a user.

        :param request: The request.
        :raise UserError: Exception raised when something is not valid.
        """
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Validate", auto_assign=True):
            if request.state == "pending":
                # Get current validation sequence
                stage, message, validator_id = request._get_validation_stage()
                if stage:
                    validator = {
                        "stage_id": stage.stage_id.id,
                        "validator_id": validator_id,
                        "date_validated": fields.Datetime.now(),
                    }
                    vals = {
                        "validator_ids": [(Command.create(validator))],
                        "last_validated_by_id": validator_id,
                        "date_validated": fields.Datetime.now(),
                        "assign_to_id": None,
                    }
                    if message == "FINAL":
                        # Mark previous activity as 'done'
                        request.last_activity_id.action_done()
                        # Create apply changes activity
                        activity_type = "spp_change_request.apply_changes_activity"
                        summary = _("For Application of Changes")
                        note = _(
                            "The change request is now fully validated. It is now submitted "
                            + "for final application of changes."
                        )
                        request._generate_activity(activity_type, summary, note)

                        vals.update({"state": "validated"})
                    # Update the change request
                    request.update(vals)

                    # Update the live data if the user has the access
                    if self.AUTO_APPLY_CHANGES and message == "FINAL" and self.auto_apply_conditions():
                        is_exception = False
                        message = ""
                        try:
                            self.action_apply()
                        except UserError as e:
                            message = _("User %(user)s does not have access to apply changes. %(error)s") % {
                                "user": self.env.user.name,
                                "error": repr(e),
                            }
                            is_exception = True
                        except Exception as e:
                            message = _(
                                "An error was encountered in applying the changes: %s",
                                repr(e),
                            )
                            is_exception = True

                        if is_exception:
                            raise UserError(message)

                    if request.state == "validated":
                        title = _("Change Request Validated")
                        message = _("The change request has been fully validated")
                        kind = "success"
                        return self.show_notification(title, message, kind)

                    if request.state == "applied":
                        title = _("Change Request Applied")
                        message = _("The change request has been validated and the changes has been applied")
                        kind = "success"
                        return self.show_notification(title, message, kind)

                    title = _("Change Request Partially Validated")
                    message = _("The change request has been partially validated")
                    kind = "success"
                    return self.show_notification(title, message, kind)

                else:
                    raise ValidationError(message)
            else:
                raise ValidationError(_("The request to be validated must be in submitted state."))
        return

    def action_apply(self):
        """
        This method is called when the Change Request is applied to the live data.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_apply"
                type="object"
            />

        :raise ValidationError: Exception raised when something is not valid.
        """
        for rec in self:
            rec._apply(rec.change_request_id)

    def _apply(self, request):
        """
        This method is used to apply the change request.

        :param request: The request.
        """
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Apply", auto_assign=True):
            if request.state == "validated":
                # Apply Changes to Live Data
                self.update_live_data()
                # Update CR record
                request.update(
                    {
                        "applied_by_id": self.env.user,
                        "date_applied": fields.Datetime.now(),
                        "assign_to_id": None,
                        "state": "applied",
                    }
                )
                # Mark previous activity as 'done'
                request.last_activity_id.action_done()

            else:
                raise ValidationError(_("The request must be in validated state for changes to be applied."))

    def action_cancel(self):
        """
        This method is called when the Change Request is applied to the live data.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_cancel"
                type="object"
            />

        :raise ValidationError: Exception raised when something is not valid.
        """
        self.ensure_one()

        form_id = self.env.ref("spp_change_request.change_request_cancel_wizard").id
        action = {
            "name": _("Cancel Change Request"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.change.request.cancel.wizard",
            "target": "new",
            "context": {
                "change_request_id": self.change_request_id.id,
            },
        }
        return action

    def _cancel(self, request):
        """
        This method is used to cancel the change request.

        :param request: The request.
        :return:
        """
        self.ensure_one()
        if request.state in ("draft", "pending", "rejected", "validated"):
            # Mark previous activity as 'done'
            request.last_activity_id.action_done()
            # Create validation activity
            activity_type = "spp_change_request.cancel_activity"
            summary = _("Change Request Cancelled")
            note = _("The change request was cancelled by %s.", self.env.user.name)
            request._generate_activity(activity_type, summary, note)

            # Update the Request
            request.update(
                {
                    "state": "cancelled",
                    "cancelled_by_id": self.env.user.id,
                    "date_cancelled": fields.Datetime.now(),
                    "validator_ids": [(Command.clear())],
                }
            )
        else:
            raise UserError(_("The request to be cancelled must be in draft, pending, or rejected validation state."))

    def action_reset_to_draft(self):
        """
        This method is called when the Change Request is applied to the live data.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_reset_to_draft"
                type="object"
            />

        :raise ValidationError: Exception raised when something is not valid.
        """
        for rec in self:
            rec._reset_to_draft(rec.change_request_id)

    def _reset_to_draft(self, request):
        """
        This method is used to reset to draft the change request.

        :param request: The request.
        :return:
        """
        self.ensure_one()

        if request.state == "rejected":
            # Mark previous activity as 'done'
            request.last_activity_id.action_done()
            # Create validation activity
            activity_type = "spp_change_request.reset_draft_activity"
            summary = _("CR Reset to Draft")
            note = _("The change request was reset to draft.")
            request._generate_activity(activity_type, summary, note)

            # Update the Request
            request.update(
                {
                    "date_requested": fields.Datetime.now(),
                    "reset_to_draft_by_id": self.env.user.id,
                    "state": "draft",
                    "validator_ids": [(Command.clear())],
                }
            )
        else:
            raise UserError(_("The request to be cancelled must be in draft, pending, or rejected validation state."))

    def action_reject(self):
        """
        This method is called when the Change Request is Reset to Draft by a user.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_reset_to_draft"
                type="object"
            />
        """
        self.ensure_one()

        form_id = self.env.ref("spp_change_request.change_request_reject_wizard").id
        action = {
            "name": _("Reject Change Request"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.change.request.reject.wizard",
            "target": "new",
            "context": {
                "change_request_id": self.change_request_id.id,
            },
        }
        return action

    def _on_reject(self, request, rejected_remarks: str):
        """
        This method is used to reject the change request.

        :param request: The request.
        :param rejected_remarks: the reason for the rejection
        :return:

        :raise UserError: Exception raised when something is not valid.
        """
        self.ensure_one()
        # Check if CR is assigned to current user
        if request._check_user("Reject", auto_assign=True):
            if request.state in ("draft", "pending"):
                # Mark previous activity as 'done'
                request.last_activity_id.action_done()
                # Create validation activity
                activity_type = "spp_change_request.reject_activity"
                summary = _("Change Request Rejected")
                note = _("The change request was rejected by %s.", self.env.user.name)
                request._generate_activity(activity_type, summary, note)

                # Update the Request
                request.update(
                    {
                        "state": "rejected",
                        "rejected_remarks": rejected_remarks,
                        "rejected_by_id": self.env.user.id,
                        "date_rejected": fields.Datetime.now(),
                        # "validator_ids": [(Command.clear())],
                    }
                )
            else:
                raise UserError(_("The request to be rejected must be in draft or pending validation state."))

    def _copy_group_member_ids(self, group_id_field, group_ref_field="registrant_id"):
        for rec in self:
            for mrec in rec[group_ref_field].group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                group_members = {
                    group_id_field: rec.id,
                    "individual_id": mrec.individual.id,
                    "kind_ids": kind_ids,
                }
                self.env["spp.change.request.group.members"].create(group_members)

    def copy_group_member_ids_condition(self):
        """Conditions to copy group members

        Overwrite this function to the inherited model to add
        condition when copying a group member.
        Do not overwrite or override if no conditions needed.

        example:
            def copy_group_member_ids_condition:
                if self.state == 'draft':
                    return True
                return False

        NOTE: always return True or False
        """
        return True

    def copy_group_member_ids(
        self,
        group_id_field,
        group_ref_field="registrant_id",
        model_name="spp.change.request.group.members",
        condition_function=copy_group_member_ids_condition,
    ):
        """Copy group members

        :param group_id_field str: name of the field
        :param group_ref_field str: name of the reference field, default value is 'registrant_id'
        :param model_name str/list: name or list of model names, default value is 'spp.change.request.group.members'
        :param condition_function method: method to add conditions, default value is copy_group_member_ids_condition

        :return:

        :example:
            self.copy_group_member_ids("group_member_id")
            self.copy_group_member_ids("group_member_id", group_ref_field="registrant_id")
            self.copy_group_member_ids("group_member_id", model_name="spp.change.request")

            def my_condition(self):
                if self.state == 'draft':
                    return True
                return False

            self.copy_group_member_ids("group_member_id", condition_function=my_condition)

        """
        for rec in self:
            for mrec in rec[group_ref_field].group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                if condition_function(self):
                    group_members = {
                        group_id_field: rec.id,
                        "individual_id": mrec.individual.id,
                        "kind_ids": kind_ids,
                    }
                    if isinstance(model_name, str):
                        self.env[model_name].create(group_members)
                    else:
                        for model in model_name:
                            self.env[model].create(group_members)

    def open_applicant_details_form(self):
        """
        Get and opens the form view of the applicant_id to view details

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_applicant_details_form"
                type="object"
            />

        NOTE:
        - To add or modify some key-value pair, either call or super this function

        example:
            def open_applicant_details_form(self):
                action = super().open_applicant_details_form()

                action.update({'key': 'value'})

                return action

        :return dict action: form view action

        :raise:
        """
        self.ensure_one()
        res_id = self.applicant_id.id
        form_id = self.env.ref("g2p_registry_individual.view_individuals_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
            "hide_from_cr": 1,
        }
        action.update(
            {
                "name": _("Applicant Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action

    def open_user_assignment_wiz(self):
        """
        Called whenever a user reassign the CR to him/her or to other user

        Reassign a CR to current user if CR is assigned to other user else
        Opens a wizard form to show a selection of users to be reassign

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_user_assignment_wiz"
                type="object"
            />

        :return: action

        :raise UserError: Exception raised when something is not valid.
        """
        for rec in self:
            is_admin = self.env.user.has_group("spp_change_request.group_spp_change_request_administrator")
            assign_self = False
            if rec.change_request_id.assign_to_id:
                if rec.change_request_id.assign_to_id.id != self.env.user.id:
                    if self.env.user.id == self.change_request_id.create_uid:
                        assign_self = True
                    elif is_admin:
                        assign_self = False
                    else:
                        raise ValidationError(_("You're not allowed to re-assign this CR."))
            else:
                assign_self = True
            if not assign_self:
                form_id = self.env.ref("spp_change_request.change_request_user_assign_wizard").id
                action = {
                    "name": _("Assign Change Request to User"),
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "view_id": form_id,
                    "view_type": "form",
                    "res_model": "spp.change.request.user.assign.wizard",
                    "target": "new",
                    "context": {
                        "curr_assign_to_id": rec.change_request_id.assign_to_id.id,
                        "change_request_id": rec.change_request_id.id,
                    },
                }
                return action
            else:
                self.change_request_id.assign_to_user(self.env.user)

    def open_user_assignment_to_wiz(self):
        """
        Called whenever a user reassign the CR to him/her or to other user

        Reassign a CR to current user if CR is assigned to other user else
        Opens a wizard form to show a selection of users to be reassign

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_user_assignment_to_wiz"
                type="object"
            />

        :return: action

        :raise UserError: Exception raised when something is not valid.
        """
        for rec in self:
            form_id = self.env.ref("spp_change_request.change_request_user_assign_wizard").id
            action = {
                "name": _("Assign Change Request to User"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "view_id": form_id,
                "view_type": "form",
                "res_model": "spp.change.request.user.assign.wizard",
                "target": "new",
                "context": {
                    "curr_assign_to_id": rec.change_request_id.assign_to_id.id,
                    "change_request_id": rec.change_request_id.id,
                    "assign_to": True,
                },
            }
            return action

    @api.depends("assign_to_id")
    def _compute_current_user_assigned(self):
        """
        Gets the current user assigned on the Change Request

        :return:
        :raise:
        """
        for rec in self:
            rec.current_user_assigned = False
            if self.env.context.get("uid", False) == rec.assign_to_id.id:
                rec.current_user_assigned = True

    def check_required_documents(self, additional_required_doc_type=None):
        """
        This method verifies that documents with the category specified in :attribute:`REQUIRED_DOCUMENT_TYPE`
        are attached to the change request.

        :raise ValidationError: Exception raised when documents are missing
        """
        for directories in self.dms_directory_ids:
            file_ids_child = []

            if directories.child_directory_ids:
                for child_directories in directories.child_directory_ids:
                    file_ids_child = child_directories.file_ids.mapped("category_id.id")

            file_ids = directories.file_ids.mapped("category_id.id")
            for child_ids in file_ids_child:
                file_ids.append(child_ids)

            missing_docs = []

            for doc in self.REQUIRED_DOCUMENT_TYPE:
                document = self.env.ref(doc)
                if document.id not in file_ids:
                    missing_docs.append(document.name)

            if additional_required_doc_type:
                for doc in additional_required_doc_type:
                    document = self.env.ref(doc)
                    if document.id not in file_ids:
                        missing_docs.append(document.name)

            if missing_docs:
                if len(missing_docs) > 1:
                    raise ValidationError(
                        _(
                            "The required documents %s are missing.",
                            ", ".join(missing_docs),
                        )
                    )
                else:
                    raise ValidationError(
                        _(
                            "The required document %s is missing.",
                            ", ".join(missing_docs),
                        )
                    )

    def action_attach_documents(self):
        for rec in self:
            # TODO: Get the directory_id based on document type
            # Get the first directory for now
            if rec.dms_directory_ids:
                directory_id = rec.dms_directory_ids[0].id
                form_id = self.env.ref("spp_change_request.view_dms_file_spp_custom_form").id
                dms_context = {"default_directory_id": directory_id}
                action = {
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "view_id": form_id,
                    "view_type": "form",
                    "res_model": "spp.dms.file",
                    "target": "new",
                    "context": dms_context,
                }
                category_name = "Other Documents"
                if self.env.context.get("category_id"):
                    category_id = self.env.context.get("category_id")
                    category = self.env["spp.dms.category"].search([("id", "=", category_id)])
                    if category:
                        dms_context.update(
                            {
                                "default_category_id": category.id,
                                "category_readonly": True,
                            }
                        )
                        category_name = category.name
                    else:
                        raise UserError(_("The required document category is not configured."))

                default_cr_id_field = self._get_default_change_request_id()
                dms_context.update({default_cr_id_field: rec.id})
                _logger.debug("action_attach_documents dms_context: %s", dms_context)
                action.update(
                    {
                        "name": _("Upload Document: %s", category_name),
                        "context": dms_context,
                    }
                )
                return action
            else:
                raise UserError(_("There are no directories defined for this change request."))

    def _get_default_change_request_id(self):
        """
        Get the default field name for change request id.
        Must be overriden in the inheriting model.
        """
        return "default_change_request_id"

    def open_registrant_details_form(self):
        """
        Opens a modal form that consists of registrant's details

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_registrant_details_form"
                type="object"
            />

        NOTE:
        - This function is used on several files. Be careful on updating this function.
        - To add or modify some key-value pair, either call or super this function

        example:
            def open_registrant_details_form(self):
                action = super().open_registrant_details_form()

                action.update({'key': 'value'})

                return action

        :return dict action: form view action

        :raise:
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

    def show_notification(self, title, message, kind):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Change Request Validated"),
                "message": message,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
                "sticky": True,
                "type": kind,
            },
        }
