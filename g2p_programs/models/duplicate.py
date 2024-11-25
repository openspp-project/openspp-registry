from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class G2PDuplicateProgramMembership(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "g2p.program.membership.duplicate"
    _description = "Program Membership duplicate"
    _order = "id desc"

    beneficiary_ids = fields.Many2many("g2p.program_membership", string="Beneficiaries")
    state = fields.Selection(selection=[("duplicate", "Duplicate"), ("not_duplicate", "Not Duplicate")])
    deduplication_manager_id = fields.Integer("Deduplication Manager")
    reason = fields.Char("Deduplication Reason")
    comment = fields.Text("Deduplication Comment")

    @api.onchange("beneficiary_ids")
    def on_beneficiaries_change(self):
        origin_length = len(self._origin.beneficiary_ids.ids)
        new_length = len(self.beneficiary_ids.ids)
        if new_length < origin_length:
            raise ValidationError(_("Can't delete duplicated membership"))
