# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging
import random
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import constants

_logger = logging.getLogger(__name__)


class G2PEntitlement(models.Model):
    _name = "g2p.entitlement"
    _description = "Entitlement"
    _order = "partner_id asc,id desc"
    _check_company_auto = True

    @api.model
    def _generate_code(self):
        return str(uuid4())[4:-8][3:]

    name = fields.Char(compute="_compute_name")
    code = fields.Char(default=lambda x: x._generate_code(), required=True, readonly=True, copy=False)

    ern = fields.Char(
        compute="_compute_generate_ern",
        string="ERN",
        # required=True,
        readonly=True,
        copy=False,
        store=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    cycle_id = fields.Many2one("g2p.cycle", required=True)
    program_id = fields.Many2one("g2p.program", related="cycle_id.program_id")

    valid_from = fields.Date(required=False)
    valid_until = fields.Date(default=lambda self: fields.Date.add(fields.Date.today(), years=1))

    is_cash_entitlement = fields.Boolean("Cash Entitlement", default=False)
    currency_id = fields.Many2one("res.currency", readonly=True, related="journal_id.currency_id")
    initial_amount = fields.Monetary(required=True, currency_field="currency_id")
    transfer_fee = fields.Monetary(currency_field="currency_id", default=0.0)
    balance = fields.Monetary(compute="_compute_balance")  # in company currency
    # TODO: implement transactions against this entitlement

    journal_id = fields.Many2one(
        "account.journal",
        "Disbursement Journal",
        store=True,
        compute="_compute_journal_id",
    )
    disbursement_id = fields.Many2one("account.payment", "Disbursement Journal Entry")
    service_fee_disbursement_id = fields.Many2one("account.payment", "Service Fee Journal Entry")

    date_approved = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_validation", "Pending Approval"),
            ("approved", "Approved"),
            ("trans2FSP", "Transferred to FSP"),
            ("rdpd2ben", "Redeemed/Paid to Beneficiary"),
            ("rejected1", "Rejected: Beneficiary didn't want the entitlement"),
            ("rejected2", "Rejected: Beneficiary account does not exist"),
            ("rejected3", "Rejected: Other reason"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
        "Status",
        default="draft",
        copy=False,
    )

    payment_ids = fields.One2many("g2p.payment", "entitlement_id", string="Payments")
    payment_status = fields.Selection(
        [("paid", "Paid"), ("notpaid", "Not Paid")], compute="_compute_payment_status"
    )
    payment_date = fields.Date(compute="_compute_payment_status")

    _sql_constraints = [
        (
            "unique_entitlement_code",
            "UNIQUE(code)",
            "The entitlement code must be unique.",
        ),
    ]

    @api.constrains("valid_from", "valid_until")
    def _check_valid_dates(self):
        for record in self:
            if record.valid_until and record.valid_from and record.valid_until < record.valid_from:
                raise ValidationError(
                    _('The "Valid Until" date cannot be earlier than the "Valid From" date.')
                )

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        group_g2p_admin = self.env.user.has_group("g2p_registry_base.group_g2p_admin")
        if not group_g2p_admin:
            if view_type != "search":
                group_g2p_registrar = self.env.user.has_group("g2p_registry_base.group_g2p_registrar")
                g2p_program_validator = self.env.user.has_group("g2p_programs.g2p_program_validator")
                g2p_program_manager = self.env.user.has_group("g2p_programs.g2p_program_manager")

                if not (group_g2p_registrar or g2p_program_validator or g2p_program_manager):
                    raise ValidationError(_("You have no access in the Entitlement List View"))

        return arch, view

    def _compute_name(self):
        for record in self:
            name = _("Entitlement")
            initial_amount = f"{record.initial_amount:,.2f}"
            if record.is_cash_entitlement:
                name += " Cash [" + str(record.currency_id.symbol) + " " + initial_amount + "]"
            else:
                name += " (" + str(record.code) + ")"
            record.name = name

    @api.depends("initial_amount")
    def _compute_balance(self):
        for record in self:
            record.balance = record.initial_amount

    @api.depends("cycle_id.program_id.journal_id")
    def _compute_journal_id(self):
        for record in self:
            record.journal_id = (
                record.cycle_id
                and record.cycle_id.program_id
                and record.cycle_id.program_id.journal_id
                and record.cycle_id.program_id.journal_id.id
                or None
            )

    def _compute_payment_status(self):
        for rec in self:
            paid_payment = None
            for payment in rec.payment_ids:
                if payment.status == "paid":
                    rec.payment_status = "paid"
                    paid_payment = payment
                    break
            if not paid_payment:
                rec.payment_status = "notpaid"
                rec.payment_date = None
            if paid_payment:
                rec.payment_date = paid_payment.payment_datetime

    @api.depends("state")
    def _compute_generate_ern(self):
        for rec in self:
            if rec.state == "approved":
                random_number = str(random.randint(1, 10**10 - 1)).zfill(10)
                rec.ern = random_number
            else:
                rec.ern = False

    @api.autovacuum
    def _gc_mark_expired_entitlement(self):
        self.env["g2p.entitlement"].search(
            ["&", ("state", "=", "approved"), ("valid_until", "<", fields.Date.today())]
        ).write({"state": "expired"})

    def can_be_used(self):
        # expired state are computed once a day, so can be not synchro
        return self.state == "approved" and self.valid_until >= fields.Date.today()

    def unlink(self):
        if self:
            to_delete = self.filtered(lambda x: x.state == "draft")
            if to_delete:
                # TODO: Need to add the logic if any one entitlements within the cycle have been approved
                # to restrict the delete records even in the draft state.
                return super(G2PEntitlement, to_delete).unlink()
            else:
                raise ValidationError(_("Only draft entitlements are allowed to be deleted"))

    def approve_entitlement(self):
        ent_program_list = []
        for rec in self:
            if rec.program_id not in ent_program_list:
                ent_program_list.append(rec.program_id)
        # TODO: To be remove in case of multiple managers are enabled.
        if len(ent_program_list) > 1:
            raise ValidationError(
                _("You can approve any number of entitlement cycles only from a specific program at a time")
            )
        ent_manager = self.program_id.get_manager(constants.MANAGER_ENTITLEMENT)

        if ent_manager:
            state_err, message = ent_manager.approve_entitlements(self)

            if state_err > 0:
                kind = "danger"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Entitlement"),
                        "message": message,
                        "sticky": False,
                        "type": kind,
                        "next": {
                            "type": "ir.actions.act_window_close",
                        },
                    },
                }

        else:
            raise UserError(_("No Entitlement Manager defined."))

    def open_entitlement_form(self):
        return self.program_id.get_manager(constants.MANAGER_ENTITLEMENT).open_entitlement_form(self)

    def open_disb_form(self):
        for rec in self:
            if rec.disbursement_id:
                res_ids = [rec.disbursement_id.id]
                view_mode = "form"
                view_id = self.env.ref("account.view_account_payment_form").id
                if rec.service_fee_disbursement_id:
                    res_ids.append(rec.service_fee_disbursement_id.id)
                    view_mode = "tree"
                    view_id = self.env.ref("account.view_account_payment_tree").id
                domain = [("id", "in", res_ids)]
                return {
                    "name": "Disbursement",
                    "view_mode": view_mode,
                    "res_model": "account.payment",
                    # "res_id": res_id,
                    "view_id": view_id,
                    "type": "ir.actions.act_window",
                    "domain": domain,
                    "target": "current",
                }
