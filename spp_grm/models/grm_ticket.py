import logging
from email.utils import parseaddr

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPGRMTicket(models.Model):
    _name = "spp.grm.ticket"
    _description = "Grievance Redress Mechanism Ticket"
    _rec_name = "number"
    _rec_names_search = ["number", "name"]
    _order = "priority desc, sequence, number desc, id desc"
    _mail_post_access = "read"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Create a new ticket from an inbound email"""
        _logger.debug("Creating new ticket from email")
        # Extract values from the email
        subject = msg_dict.get("subject") or "No Subject"
        body = msg_dict.get("body") or "No Content"
        email_from = msg_dict.get("email_from")
        email_address = parseaddr(email_from)[1]
        _logger.debug(f"Email from: {email_address}")
        # TODO: What to do if the registrant is a group?
        partner = self.env["res.partner"].search([("email", "=", email_address)], limit=1)
        if not partner:
            self._send_custom_error_notification(email_address, subject, email_from)
            _logger.warning(
                "No matching registrant found for email: %s. Email processed but a ticket is not created."
                % email_address
            )

        # Prepare default values for the new ticket
        vals = {
            "name": subject,
            "description": body,
            "partner_id": partner.id if partner else False,
            "partner_email": email_from,
            "channel_id": self.env.ref("spp_grm.grm_ticket_channel_email").id,
            "priority": "1",  # Default priority
        }

        if custom_values:
            vals.update(custom_values)

        # Create the new GRM ticket
        ticket = super().message_new(msg_dict, custom_values=vals)
        if ticket:
            _logger.info(f"New ticket created from email: {ticket.number}")
        else:
            _logger.info("No ticket was created from email.")
        return ticket

    def message_update(self, msg_dict, update_vals=None):
        """Update an existing ticket from an inbound email reply"""
        res = super().message_update(msg_dict, update_vals=update_vals)
        _logger.info(f"Ticket {self.number} updated from email")
        return res

    def _send_custom_error_notification(self, email_address, subject, email_from):
        """Send a custom email notification to the sender of the email if no registrant is found.
        :param email_address: The email address of the sender
        :param subject: The subject of the email
        :param email_from: The email address of the recipient
        """
        mail_values = {
            "subject": subject,
            "body_html": """
                <p>Dear Sender,</p>
                <p>We could not process your request because your email address <strong>%s</strong> is not
                in our record of registrants.</p>
                <p>Kind Regards</p>
            """
            % email_address,
            "email_to": email_address,
            "email_from": email_from,
        }

        # Send the email
        mail = self.env["mail.mail"].create(mail_values)
        mail.send()

    def _default_stage_id(self):
        stages = self.env["spp.grm.ticket.stage"].search([])
        if stages:
            return stages[0].id
        return None

    number = fields.Char(string="Ticket number", default="/", readonly=True)
    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        index=True,
        compute="_compute_user_id",
        store=True,
        readonly=False,
    )
    stage_id = fields.Many2one(
        comodel_name="spp.grm.ticket.stage",
        string="Stage",
        default=_default_stage_id,
        store=True,
        readonly=False,
        ondelete="restrict",
        tracking=True,
        group_expand="_read_group_stage_ids",
        copy=False,
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Registrant", required=True, domain="[('is_registrant', '=', True)]"
    )
    partner_email = fields.Char(string="Email", related="partner_id.email", store=True)
    last_stage_update = fields.Datetime(default=fields.Datetime.now)
    assigned_date = fields.Datetime()
    closed_date = fields.Datetime()
    closed = fields.Boolean(related="stage_id.closed")
    unattended = fields.Boolean(related="stage_id.unattended", store=True)
    tag_ids = fields.Many2many(comodel_name="spp.grm.ticket.tag", string="Tags")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    channel_id = fields.Many2one(comodel_name="spp.grm.ticket.channel", string="Channel")
    category_id = fields.Many2one(
        comodel_name="spp.grm.ticket.category",
        string="Category",
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        default="1",
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "spp.grm.ticket")],
        string="Media Attachments",
    )
    color = fields.Integer(string="Color Index")
    kanban_state = fields.Selection(
        selection=[
            ("normal", "Default"),
            ("done", "Ready for next stage"),
            ("blocked", "Blocked"),
        ],
    )
    sequence = fields.Integer(
        index=True,
        default=10,
        help="Gives the sequence order when displaying a list of tickets.",
    )
    active = fields.Boolean(default=True)

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.number + " - " + rec.name))
        return res

    def _creation_subtype(self):
        return self.env.ref("spp_grm.grm_tck_created")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            proceed = True
            if not vals.get("partner_id"):
                proceed = False
            else:
                if vals.get("number", "/") == "/":
                    vals["number"] = self._prepare_ticket_number()
                _logger.debug(f"Creating ticket {vals['number']}")
                if vals.get("user_id") and not vals.get("assigned_date"):
                    vals["assigned_date"] = fields.Datetime.now()
        if proceed:
            return super().create(vals_list)

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number()
        res = super().copy(default)
        return res

    def write(self, vals):
        for _ticket in self:
            now = fields.Datetime.now()
            if vals.get("stage_id"):
                stage = self.env["spp.grm.ticket.stage"].browse([vals["stage_id"]])
                vals["last_stage_update"] = now
                if stage.closed:
                    vals["closed_date"] = now
            if vals.get("user_id"):
                vals["assigned_date"] = now
        return super().write(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Read group method for stage_id field."""
        return stages.search(domain, order=order)

    def assign_to_me(self):
        self.write({"user_id": self.env.user.id})

    def _prepare_ticket_number(self):
        # Generate ticket number
        return self.env["ir.sequence"].next_by_code("spp.grm.ticket.sequence")

    def get_portal_url(self):
        """Get the URL for the ticket's portal page."""
        self.ensure_one()
        return "/my/tickets/%s" % self.id

    def send_ticket_confirmation_email(self, ticket):
        """Send the ticket submission confirmation email."""
        template = self.env.ref("spp_grm.ticket_submission_confirmation", raise_if_not_found=False)
        if template:
            template.sudo().send_mail(
                ticket.id,
                force_send=True,
                email_values={
                    "email_to": ticket.partner_id.email,
                },
            )
        else:
            _logger.warning("Email template not found: spp_grm.ticket_submission_confirmation")
