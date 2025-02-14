# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestBase(models.Model):
    """
    ChangeRequestBase is the base model for all change requests.
    The object containing the change request details points to this model.

    Every change requests have a DMS folder associated where the documents are stored.

    The change request is assigned to a user who is responsible for the change request.

    A change request can be only deleted if it is in draft state and by its original submitter.

    The change request status can evolve as follows:

    .. graphviz::

       digraph {
          "draft" -> "pending";
          "draft" -> "cancelled";
          "pending" -> "validated";
          "validated" -> "validated";
          "validated" -> "applied";
          "validated" -> "rejected";
          "rejected" -> "pending";
          "rejected" -> "draft";
          "rejected" -> "cancelled";
       }

    """

    _name = "spp.change.request"
    _description = "Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    # Must be overridden in the child class with the form id of the applicant
    APPLICANT_FORM_ID = ""
    ADMIN_GROUP_NAME = ""

    name = fields.Char("Request #", required=True, default="NEW")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    date_requested = fields.Datetime()  # Date the change request was submitted
    request_type = fields.Selection(selection="_selection_request_type_ref_id", required=True)
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
    )

    request_type_ref_id = fields.Reference(string="Change Request Template", selection="_selection_request_type_ref_id")
    validator_ids = fields.One2many(
        "spp.change.request.validators", "request_id", "Validation Records"
    )  #: List of validators that validated the change request
    assign_to_id = fields.Many2one("res.users", "Assigned to")  #: current assigned user
    last_validated_by_id = fields.Many2one("res.users", "Validated by")  #: last user that validated the change request
    date_validated = fields.Datetime()  #: last date the change request has been validated

    # TODO: Record the next validation sequence
    next_validation_sequence_id = fields.Many2one(
        "spp.change.request.validation.sequence", "Next Validation Sequence"
    )  #: When the change request is pending validation, this store the next required validation in the sequence

    applied_by_id = fields.Many2one("res.users", "Applied by")  #: user that applied the change request
    date_applied = fields.Datetime()  #: date the change request was applied
    rejected_by_id = fields.Many2one("res.users", "Rejected by")  #: user that rejected the change request
    date_rejected = fields.Datetime()  #: date the change request was rejected
    rejected_remarks = fields.Text("Rejection Remarks")  #: remarks of why the change request was rejected

    last_activity_id = fields.Many2one("mail.activity")

    # TODO: @edwin: can we rename this status?
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Validation"),
            ("validated", "Validated"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        "Status",
        required=True,
        readonly=True,
        default="draft",
    )  #: status of the change request

    cancelled_by_id = fields.Many2one("res.users", "Cancelled by")  #: user that cancelled the change request
    date_cancelled = fields.Datetime()  #: date the change request was cancelled

    reset_to_draft_by_id = fields.Many2one(
        "res.users", "Reset to Draft by"
    )  #: user that reset the change request to draft
    date_reset_to_draft = fields.Datetime()  #: date the change request was reset to draft

    validation_group_id = fields.Many2one(
        "res.groups",
        string="Change Request Validation Group",
        compute="_compute_validation_group_id",
        store=True,
    )

    current_user_assigned = fields.Boolean(compute="_compute_current_user_assigned", default=False)

    # DMS Directories
    dms_directory_ids = fields.One2many(
        "spp.dms.directory",
        "change_request_id",
        string="DMS Directories",
        auto_join=True,
    )

    @api.onchange("request_type")
    def _onchange_request_type(self):
        """
        Called whenever request_type field is changed.
        Clear the registrant_id field.
        """
        self.registrant_id = None

    @api.model
    def create(self, vals):
        """
        Creates a record for this model and generate activity

        Usage:

        - Add/Update key-value pair on vals before calling super
        - Generate activity and add the activity to the result of super

        :param dict vals: field name and value pair

        :return recordset res:

        :raise:
        """

        # Assign the CR to the current user by default
        if "assign_to_id" not in vals or vals["assign_to_id"] is None:
            vals["assign_to_id"] = self.env.user.id
        vals["name"] = self.env["ir.sequence"].next_by_code("spp.change.request.num")
        res = super().create(vals)
        # Create pending validation activity
        activity_type = "spp_change_request_base.pending_validation_activity"
        summary = _("For Pending Validation")
        note = _("A new change request was submitted. The next step will set this request to 'Pending Validation'.")
        res._generate_activity(activity_type, summary, note)
        return res

    def unlink(self):
        """
        This method overrides the default unlink method of model.

        Unlink Change request type reference of the record then delete the record.
        Can only be deleted when these conditions are met:
        - state is 'draft'
        - current user is the who creates the record

        :param:

        :return:

        :raise:
        """
        for rec in self:
            # Only allow the deletion of draft change requests by the user who created it
            if rec.state == "draft" and rec.create_uid == self.env.user:
                # Remove the associated CR type record
                if rec.request_type_ref_id:
                    rec.request_type_ref_id.unlink()
                return super().unlink()
            else:
                raise UserError(_("Only draft change requests can be deleted by its creator."))

    @api.model
    def _selection_request_type_ref_id(self):
        return []

    def open_change_request_form(self, target="current", mode="readonly"):
        """
        Get and opens the form view or validation form view of the selected request type of the Change Request
        based on the context passed in env

        Returns an error display notification when no request type is selected.

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="open_change_request_form"
                type="object"
            />

        NOTE: To change the values of a parameter and use it to xml, I suggest you to create a new function and
              call this function with different arguments

        example:
            def new_open_request_form(self):
                return self.open_change_request_form(target="<other_value>", mode="<other_value>")

            <button
                name="new_open_request_form"
                type="object"
            />

        :param str target:
        :param str readonly:

        :return dict action: form view action

        :raise:
        """
        self.ensure_one()
        if self.request_type_ref_id:
            # Get the res_model and res_id from the request_type_ref_id (reference field)
            request_type_ref_id = str(self.request_type_ref_id)
            s = request_type_ref_id.find("(")
            res_model = request_type_ref_id[:s]
            res_id = self.request_type_ref_id.id
            if res_id:
                form_id = self.env[res_model].get_request_type_view_id()
                if self._context.get("show_validation_form"):
                    form = self.env.ref(self.request_type_ref_id.VALIDATION_FORM) or None
                    if form:
                        form_id = form.id
                action = self.env[res_model].get_formview_action()
                context = {
                    "create": False,
                }
                action.update(
                    {
                        "views": [(form_id, "form")],
                        "res_id": res_id,
                        "target": target,
                        "context": context,
                        "flags": {"mode": mode},
                    }
                )
                return action

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ERROR!"),
                "message": _("The Request Type field must be filled-up."),
                "sticky": False,
                "type": "danger",
            },
        }

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
            is_admin = self.env.user.has_group(self.ADMIN_GROUP_NAME)
            assign_self = False
            if rec.assign_to_id:
                if rec.assign_to_id.id != self.env.user.id:
                    if self.env.user.id == self.create_uid:
                        assign_self = True
                    elif is_admin:
                        assign_self = False
                    else:
                        raise ValidationError(_("You're not allowed to re-assign this CR."))
            else:
                assign_self = True
            if not assign_self:
                form_id = self.env.ref("spp_change_request_base.change_request_user_assign_wizard").id
                action = {
                    "name": _("Assign Change Request to User"),
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "view_id": form_id,
                    "view_type": "form",
                    "res_model": "spp.change.request.user.assign.wizard",
                    "target": "new",
                    "context": {"curr_assign_to_id": rec.assign_to_id.id},
                }
                return action
            else:
                self.assign_to_user(self.env.user)

    def assign_to_user(self, user):
        """
        Add user to assign_to_id field when certain conditions are met

        :param res.user user: record of the user.

        :return:
        :rtype:

        :example:

        >>> self.assign_to_user(self.env.user)

        :raise UserError: Exception raised when something is not valid.
        """

        self.ensure_one()
        user_ok = False
        # Fully validated CRs will proceed
        if self.state in ["draft", "validated", "rejected"]:
            # TODO: User must be a member of administrator and validator HQ
            user_ok = True
        else:
            # Check if user is a member of validators in the validation sequence config
            if self.request_type_ref_id and self.request_type_ref_id.validation_ids:
                for mrec in self.request_type_ref_id.validation_ids:
                    if mrec.validation_group_id.id in user.groups_id.ids:
                        user_ok = True
                        break
            else:
                raise UserError(_("This change request does not have any validation sequence defined."))
        if user_ok:
            self.update(
                {
                    "assign_to_id": user.id,
                }
            )
        else:
            raise UserError(
                _("Only users of groups defined in the validation sequence " "can be assigned to this change request.")
            )

    def open_request_detail(self):
        """
        Open the form view of the selected request type

        :return dict action: form view action
        """

        for rec in self:
            # Open Request Form
            mode = "edit"
            if self.env.user.id not in [self.assign_to_id.id, self.create_uid]:
                mode = "readonly"
            return rec.open_change_request_form(target="current", mode=mode)

    def create_request_detail_no_redirect(self):
        """
        Creates the request_type_ref record

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="create_request_detail_no_redirect"
                type="object"
            />

        NOTE: do not return the action of create_request_detail to not do redirection of page

        :return dict action: form view action
        """

        # Called the function without return
        self.create_request_detail()

    def create_request_detail(self):
        """
        Creates the request_type_ref record then opens the form view of the selected request type

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="create_request_detail"
                type="object"
            />

        :return dict action: form view action
        """

        for rec in self:
            if rec.state in ("draft", "pending"):
                # Set the request_type_ref_id
                res_model = rec.request_type
                # Set the dms directory
                _logger.debug("Change Request: DMS Directory Creation (%s)" % len(rec.dms_directory_ids))
                dmsval = {
                    "is_root_directory": True,
                    "name": rec.name,
                }

                # Prepare CR type model data
                cr_type_vals = {
                    "registrant_id": rec.registrant_id.id,
                    "change_request_id": rec.id,
                    "dms_directory_ids": [(Command.create(dmsval))],
                }
                cr_type_vals.update(rec._get_addl_cr_type_vals())

                # Create the change request detail record
                ref_id = self.env[res_model].create(cr_type_vals)
                directory_id = ref_id.dms_directory_ids[0].id

                self.env["spp.dms.directory"].create(
                    {
                        "name": "Applicant",
                        "parent_id": directory_id,
                        "is_root_directory": False,
                    }
                )

                dms_file_ids = rec._get_dms_file_ids()
                if dms_file_ids:
                    ref_id.update({"dms_file_ids": dms_file_ids})

                ref_id._onchange_registrant_id()
                request_type_ref_id = f"{res_model},{ref_id.id}"
                _logger.debug("DEBUG! request_type_ref_id: %s", request_type_ref_id)
                rec.update(
                    {
                        "request_type_ref_id": request_type_ref_id,
                    }
                )
                # Open Request Form
                return rec.open_change_request_form(target="current", mode="edit")
            else:
                raise UserError(_("The change request to be created must be in draft or pending validation state."))

    def _get_addl_cr_type_vals(self):
        """
        Get additional CR type values.
        Override this method in the CR type model to get the additional CR type values.

        :return: dict of additional CR type values
        """
        return {}

    def _get_dms_file_ids(self):
        """
        Get the DMS file ids.
        Override this method in the CR type model to get the DMS file ids.

        :return: list of DMS file ids
        """
        return []

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

        :raise UserError: Exception raised when no selected request type.
        """
        for rec in self:
            if rec.request_type_ref_id:
                rec.request_type_ref_id._on_submit(rec)
            else:
                raise UserError(_("The change request type must be properly filled-up."))

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
            return rec.request_type_ref_id._on_validate(rec)

    def action_apply(self):
        """
        This method is called when the Change Request is applied by a user.

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
            rec.request_type_ref_id._apply(rec)

    def action_cancel(self):
        """
        Get and opens the wizard form change_request_cancel_wizard to cancel the change request

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

        form_id = self.env.ref("spp_change_request_base.change_request_cancel_wizard").id
        action = {
            "name": _("Cancel Change Request"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.change.request.cancel.wizard",
            "target": "new",
            "context": {
                "change_request_id": self.id,
            },
        }
        return action

    def _cancel(self, request):
        """
        To cancel the change request when certain conditions are met.
        The user who cancelled the change requeest and the datetime it occured is also saved

        :param request: The request.
        :raise UserError: if state not in draft, pending, or rejected
        """
        self.ensure_one()
        if request.state in ("draft", "pending", "rejected"):
            request.update(
                {
                    "state": "cancelled",
                    "cancelled_by_id": self.env.user.id,
                    "date_cancelled": fields.Datetime.now(),
                    "validator_ids": [(Command.clear())],
                }
            )
            # Mark previous activity as 'done'
            request.last_activity_id.action_done()
        else:
            raise UserError(_("The request to be cancelled must be in draft, pending, or rejected validation state."))

    def action_reset_to_draft(self):
        """
        This method is called when the Change Request is Reset to Draft by a user.

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
            rec.request_type_ref_id._reset_to_draft(rec)

    def action_reject(self):
        """
        Opens reject wizard form change_request_reject_wizard

        Usage:
        - Add this function in the name of button with type object in XML

        example:
            <button
                name="action_reset_to_draft"
                type="object"
            />

        :param:

        :return: action
        :rtype: dict
        """

        form_id = self.env.ref("spp_change_request_base.change_request_reject_wizard").id
        action = {
            "name": _("Reject Change Request"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": form_id,
            "view_type": "form",
            "res_model": "spp.change.request.reject.wizard",
            "target": "new",
        }
        return action

    def _check_user(self, process, auto_assign=False):
        self.ensure_one()

        # if no user is assigned, assign to current user
        if not self.assign_to_id and auto_assign:
            self.assign_to_user(self.env.user)

        if self.assign_to_id:
            # Only user assigned to CR is allowed to process
            if self.assign_to_id.id == self.env.user.id:
                return True
            else:
                raise UserError(_("You are not allowed to %s this change request", process))
        else:
            raise UserError(_("There are no user assigned to this change request."))

    @api.depends("validator_ids", "state")
    def _compute_validation_group_id(self):
        """
        Called whenever there are changes in validator_ids and state field.
        Save a list of groups that are currently allowed to validate the Change Request.
        """
        for rec in self:
            if rec.state in ["draft", "pending"]:
                # Directly obtain validation_stage_ids if validator_ids are present
                validation_stage_ids = rec.validator_ids.mapped("stage_id.id") if rec.validator_ids else []

                validation_stages = (
                    rec.request_type_ref_id.validation_ids
                    if rec.request_type_ref_id and rec.request_type_ref_id.validation_ids
                    else self.env["spp.change.request.validation.sequence"].browse()
                )  # Replace 'validation.model' with the actual model name

                # Filter validation_stages based on validation_stage_ids, if any
                if validation_stage_ids:
                    validation_stages = validation_stages.filtered(lambda a: a.stage_id.id not in validation_stage_ids)  # noqa: B023

                if validation_stages:
                    rec.validation_group_id = validation_stages[0].validation_group_id

    def _get_validation_stage(self):
        """
        Gets the validation stage and message of a Change Request

        :param:.

        :return: stage, message, validator_id
        :rtype: spp.change.request.validation.stage, str, int

        :example:

        >>> self._get_validation_stage()
        """
        self.ensure_one()
        stage = None
        message = None
        validator_id = self.env.user.id
        # Get the current validators
        validation_stages = None
        validation_stage_ids = None
        if self.validator_ids:
            validation_stage_ids = self.validator_ids.mapped("stage_id.id")
        if self.request_type_ref_id.validation_ids:
            # Get the next validation sequence
            if validation_stage_ids:
                validation_stages = self.request_type_ref_id.validation_ids.filtered(
                    lambda a: a.stage_id.id not in validation_stage_ids
                )
            else:
                validation_stages = self.request_type_ref_id.validation_ids
            if validation_stages:
                if len(validation_stages) == 1:
                    message = "FINAL"
                stage = validation_stages[0]
                # Check if user is allowed to validate request
                if self.state not in ["draft", "rejected"] and validator_id not in stage.validation_group_id.users.ids:
                    message = _(
                        "You are not allowed to validate this request! Stage: %(stage)s. "
                        "Allowed Validator Group: %(group)s",
                    ) % {"stage": stage.stage_id.name, "group": stage.validation_group_id.name}
                    stage = None
            else:
                message = _("Error in validation stages. No available stage to assign to this validation.")
        else:
            message = _("There are no validators defined for this request.")
        return stage, message, validator_id

    def _generate_activity(self, activity_type, summary, note):
        self.ensure_one()
        activity_type_id = self.env.ref(activity_type).id
        next_activity = {
            "res_id": self.id,
            "res_model_id": self.env["ir.model"]._get(self._name).id,
            "user_id": self.env.user.id,
            "summary": summary,
            "note": note,
            "activity_type_id": activity_type_id,
            "date_deadline": fields.Date.today(),
        }
        activity = self.env["mail.activity"].create(next_activity)
        # Mark cancel activity as 'done' because there are no re-activation after cancellation of CR
        if activity_type == "spp_change_request_base.cancel_activity":
            activity.action_done()
            return

        # When calling action_done this return below is no longer possible as the activity will be deleted
        return self.update({"last_activity_id": activity.id})

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


class ChangeRequestValidators(models.Model):
    _name = "spp.change.request.validators"
    _description = "Change Request Validators"
    _rec_name = "validator_id"

    request_id = fields.Many2one("spp.change.request", "Change Request")
    stage_id = fields.Many2one("spp.change.request.validation.stage", "Validation Stage", required=True)
    validator_id = fields.Many2one("res.users", "Validated by", required=True)
    date_validated = fields.Datetime()


class ChangeRequestValidationSequence(models.Model):
    _name = "spp.change.request.validation.sequence"
    _description = "Change Request Validation Sequence"
    _rec_name = "stage_id"
    _order = "sequence,id"

    sequence = fields.Integer(default=10)
    request_type = fields.Selection(selection="_selection_request_type_ref_id", required=True)
    stage_id = fields.Many2one("spp.change.request.validation.stage", "Validation Stage", required=True)
    validation_group_id = fields.Many2one("res.groups", string="Change Request Validation Group")
    validation_group_state = fields.Selection(
        [
            ("source", "Source Area"),
            ("destination", "Destination Area"),
            ("both", "Apply to Both"),
        ],
        string="Validation Group Application",
        default="both",
        required=True,
    )

    @api.model
    def _selection_request_type_ref_id(self):
        return []
