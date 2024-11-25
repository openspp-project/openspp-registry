# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    # Custom Fields
    program_membership_ids = fields.One2many("g2p.program_membership", "partner_id", "Program Memberships")
    cycle_ids = fields.One2many("g2p.cycle.membership", "partner_id", "Cycle Memberships")
    entitlement_ids = fields.One2many("g2p.entitlement", "partner_id", "Entitlements")

    # Statistics
    program_membership_count = fields.Integer(
        string="# Program Memberships",
        compute="_compute_program_membership_count",
        store=True,
    )
    entitlements_count = fields.Integer(
        string="# Cash Entitlements", compute="_compute_entitlements_count", store=True
    )
    cycles_count = fields.Integer(string="# Cycles", compute="_compute_cycle_count", store=True)

    @api.depends("program_membership_ids")
    def _compute_program_membership_count(self):
        for rec in self:
            program_membership_count = self.env["g2p.program_membership"].search_count(
                [("partner_id", "=", rec.id)]
            )
            rec.update({"program_membership_count": program_membership_count})

    @api.depends("entitlement_ids")
    def _compute_entitlements_count(self):
        for rec in self:
            entitlements_count = self.env["g2p.entitlement"].search_count([("partner_id", "=", rec.id)])
            rec.update({"entitlements_count": entitlements_count})

    @api.depends("cycle_ids")
    def _compute_cycle_count(self):
        for rec in self:
            cycles_count = self.env["g2p.cycle.membership"].search_count([("partner_id", "=", rec.id)])
            rec.update({"cycles_count": cycles_count})

    @api.constrains("email")
    def _check_valid_email(self):
        for record in self:
            if record.email and not tools.single_email_re.match(record.email):
                raise ValidationError(_("Invalid Email! Please enter a valid email address."))
