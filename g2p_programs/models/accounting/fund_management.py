# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# , RedirectWarning, ValidationError, AccessError


class ProgramFundManagement(models.Model):
    _name = "g2p.program.fund"
    _description = "Program Fund Entries"
    _inherit = ["mail.thread"]
    _order = "id desc"

    # DISABLE_EDIT_DOMAIN = [("state", "=", "posted")]

    name = fields.Char("Reference Number", required=True, default="Draft")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    program_id = fields.Many2one("g2p.program", "Program", required=True)
    journal_id = fields.Many2one(
        "account.journal",
        "Disbursement Journal",
        related="program_id.journal_id",
        store=True,
    )
    account_move_id = fields.Many2one("account.move", "Journal Entry")
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        readonly=True,
        related="program_id.journal_id.currency_id",
        store=True,
    )
    remarks = fields.Text()
    date_posted = fields.Date(required=True, default=fields.Date.today)
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled")],
        "Status",
        readonly=True,
        default="draft",
    )

    @api.ondelete(at_uninstall=False)
    def _unlink_fund(self):
        count_posted_fund = 0
        for record in self:
            if record.state == "posted":
                count_posted_fund += 1
        if count_posted_fund > 0:
            raise UserError(_("This fund is already posted and cannot be deleted."))

    def post_fund(self):
        for rec in self:
            if rec.state == "draft":
                vals = {"state": "posted", "date_posted": fields.Date.today()}
                if rec.name in ("Draft", None):
                    vals.update(
                        {"name": self.env["ir.sequence"].next_by_code("program.fund.ref.num") or "NONE"}
                    )
                # TODO: Generate journal entry
                rec.update(vals)
                return {
                    "effect": {
                        "fadeout": "fast",
                        "message": _("This fund is now posted!"),
                        "type": "rainbow_man",
                    }
                }
            else:
                message = _("Only draft program funds can be posted.")
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Program Fund"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                    },
                }

    def cancel_fund(self):
        for rec in self:
            if rec.state == "draft":
                rec.update({"state": "cancelled"})
            else:
                message = _("Only draft program funds can be cancelled.")
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Program Fund"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                    },
                }

    def reset_draft(self):
        for rec in self:
            if rec.state == "cancelled":
                rec.update({"state": "draft"})
            else:
                message = _("Only cancelled program funds can be reset to draft.")
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Program Fund"),
                        "message": message,
                        "sticky": False,
                        "type": kind,  # types: success,warning,danger,info
                    },
                }
