# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestBase(models.Model):
    _name = "spp.change.request"
    _description = "Change Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char("Request #", required=True, default="Draft")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    date_requested = fields.Datetime()
    request_type = fields.Selection(
        selection="_selection_request_type_ref_id", required=True
    )
    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True)],
        required=True,
    )
    request_type_ref_id = fields.Reference(
        string="Change Request Template", selection="_selection_request_type_ref_id"
    )
    validator_ids = fields.One2many(
        "spp.change.request.validators", "request_id", "Validation Records"
    )
    appliedby_id = fields.Many2one("res.users", "Applied by")
    date_applied = fields.Datetime()
    last_activity_id = fields.Many2one("mail.activity")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending Validation"),
            ("validated", "Validated"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
        ],
        "status",
        required=True,
        readonly=True,
        default="draft",
    )

    @api.model
    def create(self, vals):
        res = super(ChangeRequestBase, self).create(vals)
        # Create pending validation activity
        activity_type = "spp_change_request.pending_validation_activity"
        summary = _("For Pending Validation")
        note = _(
            "A new change request was submitted. The next step will set this request to 'Pending Validation'."
        )
        activity = self._generate_activity(res, activity_type, summary, note)
        res["last_activity_id"] = activity.id
        return res

    @api.model
    def _selection_request_type_ref_id(self):
        return []

    def open_change_request_form(self, target="current", mode="readonly"):
        self.ensure_one()
        if self.request_type_ref_id:
            # Get the res_model and res_id from the request_type_ref_id (reference field)
            request_type_ref_id = str(self.request_type_ref_id)
            s = request_type_ref_id.find("(")
            res_model = request_type_ref_id[:s]
            res_id = self.request_type_ref_id.id
            if res_id:
                action = self.env[res_model].get_formview_action()
                context = {
                    "create": False,
                }
                action.update(
                    {
                        "views": [
                            (self.env[res_model].get_request_type_view_id(), "form")
                        ],
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
                "title": "ERROR!",
                "message": "The Request Type field must be filled-up.",
                "sticky": False,
                "type": "danger",
            },
        }

    def open_request_detail(self):
        for rec in self:
            # Open Request Form
            return rec.open_change_request_form(target="new", mode="edit")

    def create_request_detail(self):
        for rec in self:
            if rec.state in ("draft", "pending"):
                # Set the request_type_ref_id
                res_model = rec.request_type
                ref_id = self.env[res_model].create(
                    {"registrant_id": rec.registrant_id.id, "change_request_id": rec.id}
                )
                request_type_ref_id = f"{res_model},{ref_id.id}"
                _logger.debug("DEBUG! request_type_ref_id: %s", request_type_ref_id)
                rec.update(
                    {
                        "request_type_ref_id": request_type_ref_id,
                    }
                )
                # Open Request Form
                return rec.open_change_request_form(target="new", mode="edit")
            else:
                raise ValidationError(
                    _(
                        "The change request to be created must be in draft or pending validation state."
                    )
                )

    def set_pending_validation(self):
        for rec in self:
            if rec.state == "draft":
                # Mark previous activity as 'done'
                rec.last_activity_id.action_done()
                # Create validation activity
                activity_type = "spp_change_request.validation_activity"
                summary = _("For Validation")
                note = _(
                    "The change request is now set for validation. Depending on the "
                    + "validation sequence, this may be subjected to one or more validations."
                )
                activity = self._generate_activity(rec, activity_type, summary, note)

                # Update change request
                name = self.env["ir.sequence"].next_by_code("spp.change.request.num")
                rec.update(
                    {
                        "name": name,
                        "date_requested": fields.Datetime.now(),
                        "state": "pending",
                        "last_activity_id": activity.id,
                    }
                )
            else:
                raise ValidationError(
                    _(
                        "The request must be in draft state to be set under pending validation."
                    )
                )

    def validate_request(self):
        for rec in self:
            if rec.state == "pending":
                # Get current validation sequence
                stage, message, validator_id = rec._get_validation_stage()
                if stage:
                    validator = {
                        "stage_id": stage.id,
                        "validator_id": validator_id,
                        "date_validated": fields.Datetime.now(),
                    }
                    vals = {"validator_ids": [(Command.create(validator))]}
                    if message == "FINAL":
                        # Mark previous activity as 'done'
                        rec.last_activity_id.action_done()
                        # Create apply changes activity
                        activity_type = "spp_change_request.apply_changes_activity"
                        summary = _("For Application of Changes")
                        note = _(
                            "The change request is now fully validated. It is now submitted "
                            + "for final application of changes."
                        )
                        activity = self._generate_activity(
                            rec, activity_type, summary, note
                        )

                        vals.update(
                            {"state": "validated", "last_activity_id": activity.id}
                        )
                    # Update the change request
                    rec.update(vals)
                else:
                    raise ValidationError(message)
            else:
                raise ValidationError(
                    _("The request to be validated must be in submitted state.")
                )

    def apply_changes(self):
        for rec in self:
            if rec.state == "validated":
                # Apply Changes to Live Data
                rec.request_type_ref_id.update_live_data()
                # Update CR record
                rec.update(
                    {
                        "appliedby_id": self.env.user,
                        "date_applied": fields.Datetime.now(),
                        "state": "applied",
                    }
                )
                # Mark previous activity as 'done'
                rec.last_activity_id.action_done()
            else:
                raise ValidationError(
                    _(
                        "The request must be in validated state for changes to be applied."
                    )
                )

    def reject_request(self):
        for rec in self:
            if rec.state in ("draft", "pending"):
                rec.update(
                    {
                        "state": "rejected",
                    }
                )
                # Mark previous activity as 'done'
                rec.last_activity_id.action_done()
            else:
                raise ValidationError(
                    _(
                        "The request to be rejected must be in draft or pending validation state."
                    )
                )

    def _get_validation_stage(self):
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
                if validator_id not in stage.validation_group_id.users.ids:
                    message = (
                        _("You are not allowed to validate this request! Stage: %s")
                        % stage.stage_id.name
                    )
                    stage = None
            else:
                message = _(
                    "Error in validation stages. No available stage to assign to this validation."
                )
        else:
            message = _("There are no validators defined for this request.")
        return stage, message, validator_id

    def _generate_activity(self, res, activity_type, summary, note):
        activity_type_id = self.env.ref(activity_type).id
        next_activity = {
            "res_id": res.id,
            "res_model_id": self.env["ir.model"]._get(self._name).id,
            "user_id": self.env.user.id,
            "summary": summary,
            "note": note,
            "activity_type_id": activity_type_id,
            "date_deadline": fields.Date.today(),
        }
        return self.env["mail.activity"].create(next_activity)


class ChangeRequestValidators(models.Model):
    _name = "spp.change.request.validators"
    _description = "Change Request Validators"
    _rec_name = "validator_id"

    request_id = fields.Many2one("spp.change.request", "Change Request", required=True)
    stage_id = fields.Many2one(
        "spp.change.request.validation.stage", "Validation Stage", required=True
    )
    validator_id = fields.Many2one("res.users", "Validated by", required=True)
    date_validated = fields.Datetime()


class ChangeRequestValidationSequence(models.Model):
    _name = "spp.change.request.validation.sequence"
    _description = "Change Request Validation Sequence"
    _rec_name = "stage_id"
    _order = "sequence,id"

    sequence = fields.Integer(default=10)
    request_type = fields.Selection(
        selection="_selection_request_type_ref_id", required=True
    )
    stage_id = fields.Many2one(
        "spp.change.request.validation.stage", "Validation Stage", required=True
    )
    validation_group_id = fields.Many2one(
        "res.groups", string="Change Request Validation Group"
    )

    @api.model
    def _selection_request_type_ref_id(self):
        return []
