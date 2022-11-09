# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ChangeRequestTypeCustomMoveTransfer(models.Model):
    _inherit = "spp.change.request"

    @api.model
    def _selection_request_type_ref_id(self):
        selection = super()._selection_request_type_ref_id()
        new_request_type = ("spp.change.request.move.transfer", "Move/Transfer Members")
        if new_request_type not in selection:
            selection.append(new_request_type)
        return selection


class ChangeRequestMoveTransfer(models.Model):
    _name = "spp.change.request.move.transfer"
    _inherit = [
        "spp.change.request.source.mixin",
        "spp.change.request.validation.sequence.mixin",
    ]
    _description = "Move/Transfer Member Change Request Type"

    # Initialize DMS Storage
    DMS_STORAGE = "spp_change_request_move.attachment_storage_move"

    # Redefine registrant_id to set specific domain and label
    registrant_id = fields.Many2one(
        "res.partner",
        "Move/Transfer to Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )

    request_type = fields.Selection(related="change_request_id.request_type")

    # Change Request Fields
    registrant_to_move_id = fields.Many2one(
        "res.partner",
        "Individual to Move",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    kind = fields.Many2many(
        "g2p.group.membership.kind", string="Group Membership Types"
    )
    remarks = fields.Text()

    # Target Group Current Members
    move_to_group_member_ids = fields.One2many(
        "spp.change.request.group.members", "group_move_to_id", "Group Members"
    )

    # Add domain to inherited field: validation_ids
    validation_ids = fields.Many2many(
        relation="spp_change_request_move_rel", domain=[("request_type", "=", _name)]
    )

    def write(self, vals):
        res = super(ChangeRequestMoveTransfer, self).write(vals)
        if self.registrant_id:
            # Must update the spp.change.request (base) registrant_id
            self._update_registrant_id(self)
        return res

    @api.onchange("registrant_id")
    def _onchange_registrant_id(self):
        if self.move_to_group_member_ids:
            self.move_to_group_member_ids = [(Command.clear())]
        # Populate the group members
        self._copy_group_member_ids()

    def _copy_group_member_ids(self):
        for rec in self:
            _logger.info(
                "Change Request: Move/Transfer Member _copy_group_member_ids: rec: %s"
                % rec
            )
            for mrec in rec.registrant_id.group_membership_ids:
                kind_ids = mrec.kind and mrec.kind.ids or None
                group_members = {
                    "group_move_to_id": rec.id,
                    "individual_id": mrec.individual.id,
                    "kind_ids": kind_ids,
                }
                self.env["spp.change.request.group.members"].create(group_members)

    def _update_live_data(self):
        self.ensure_one()
        # Move member:registrant_to_move_id to group:registrant_id
        kinds = []
        for rec in self.kind:
            kinds.append(Command.link(rec.id))
        self.registrant_id.group_membership_ids.update(
            {
                "group": self.registrant_id.id,
                "individual": self.registrant_to_move_id.id,
                "kind": kinds,
            }
        )

    def _on_validate(self, request):
        self.ensure_one()
        # Get current validation sequence
        stage, message, validator_id = request._get_validation_stage()
        if stage:
            validator = {
                "stage_id": stage.id,
                "validator_id": validator_id,
                "date_validated": fields.Datetime.now(),
            }
            vals = {
                "validator_ids": [(Command.create(validator))],
                "validatedby_id": validator_id,
                "date_validated": fields.Datetime.now(),
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
                activity = request._generate_activity(activity_type, summary, note)

                vals.update(
                    {
                        "state": "validated",
                        "last_activity_id": activity.id,
                    }
                )
            # Update the change request
            request.update(vals)
        else:
            raise ValidationError(message)

    def open_registrant_details_form(self):
        self.ensure_one()
        res_id = self.registrant_id.id
        form_id = self.env.ref("g2p_registry_group.view_groups_form").id
        action = self.env["res.partner"].get_formview_action()
        context = {
            "create": False,
            "edit": False,
        }
        action.update(
            {
                "name": _("Member Details"),
                "views": [(form_id, "form")],
                "res_id": res_id,
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
        )
        return action
