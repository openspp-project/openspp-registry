# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group


class OpenSPPIDQueue(models.Model):
    _name = "spp.print.queue.id"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ID Queue"
    _order = "id DESC"

    JOB_SIZE = 20

    name = fields.Char("Request Name", compute="_compute_name")
    id_type = fields.Many2one("g2p.id.type", required=True)
    idpass_id = fields.Many2one("spp.id.pass")
    requested_by = fields.Many2one("res.users", required=True)
    approved_by = fields.Many2one("res.users")
    generated_by = fields.Many2one("res.users")
    printed_by = fields.Many2one("res.users")
    distributed_by = fields.Many2one("res.users")
    registrant_id = fields.Many2one("res.partner", required=True)
    area_id = fields.Many2one("spp.area", related="registrant_id.area_id", store=True)
    date_requested = fields.Date()
    date_approved = fields.Date()
    date_generated = fields.Date()
    date_printed = fields.Date()
    date_distributed = fields.Date()
    status = fields.Selection(
        [
            ("new", "New"),
            ("approved", "Approved"),
            ("generating", "Generating"),
            ("generated", "Generated"),
            ("printed", "Printed"),
            ("distributed", "Distributed"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
    )
    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")

    batch_id = fields.Many2one("spp.print.queue.batch", string="Batch")

    @api.depends("registrant_id", "idpass_id")
    def _compute_name(self):
        """
        This function is used to compute the name of the queue base on
        registrant name and template name
        """
        for rec in self:
            rec.name = f"{rec.registrant_id.name or ''} - {rec.idpass_id.name or ''}"

    def on_approve(self):
        """
        This function is used to approve or validate the request
        """
        for rec in self:
            rec.date_approved = date.today()
            rec.approved_by = self.env.user.id
            rec.status = "approved"
            message = _("%(user)s validated this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)

    def on_generate(self):
        # Make sure the ID is in the correct state before generating
        # we allow to re-generate cards
        self.generate_cards()

    def on_print(self):
        """
        This function is used to set the request as printed
        """

        # as we return the PDF, we need to make sure that there is only 1 card selected
        self.ensure_one()

        # Make sure the ID is in the correct state before printing
        if self.filtered(lambda x: x.status not in ["generated", "approved"]):
            raise ValidationError(_("ID must be approved before printing"))

        if self.filtered(lambda x: x.batch_id):
            raise ValidationError(_("ID in a batch cannot be printed individually"))

        if self.status == "approved":
            # Not generated yet, generate it
            res_id = self.generate_card(self)
        else:
            res_id = self.id_pdf

        self.date_printed = date.today()
        self.printed_by = self.env.user.id
        self.status = "printed"
        message = _("%(user)s printed this request on %(date)s.") % {
            "user": self.env.user.name,
            "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
        }
        self.save_to_mail_thread(message)
        return res_id

    def generate_cards(self):
        """
        These are used to generate the ID from the request
        """
        if self.filtered(lambda x: x.status not in ["generating", "generated", "approved", "added_to_batch"]):
            raise ValidationError(_("ID must be approved before printing"))

        for rec in self:
            rec.generate_card(rec)
            rec.status = "generated"
            date_now = datetime.now()
            message = _("%(user)s generated this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": date_now.strftime("%B %d, %Y at %H:%M"),
            }
            rec.generated_by = self.env.user.id
            rec.date_generated = date_now.date()
            rec.save_to_mail_thread(message)

    def generate_card(self, card):
        """
        Override this method to change the backend used to generate the ID card
        :param card: The Card being generated.
        :return: Call send_idpass_parameters with vals
        """
        if card.id_type.id == self.env.ref("spp_idpass.id_type_idpass").id:
            vals = {"idpass": self.idpass_id.id, "id_queue": self.id}
            self.registrant_id.send_idpass_parameters(vals)

    def on_cancel(self):
        """
        This function is used to cancel the request
        """
        if self.filtered(lambda x: x.status in ["printed", "distributed"]):
            raise ValidationError(_("ID cannot be canceled if it has been printed"))
        for rec in self:
            rec.status = "cancelled"
            message = _("%(user)s cancelled this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)

    def on_distribute(self):
        """
        This function is used to set the request as distributed
        """
        if not self.filtered(lambda x: x.status in ["printed"]):
            raise ValidationError(_("ID can only be distributed if it has been printed"))
        for rec in self:
            rec.date_distributed = date.today()
            rec.status = "distributed"
            message = _("%(user)s distributed this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.distributed_by = self.env.user.id
            rec.save_to_mail_thread(message)

    def validate_requests(self):
        """
        This function is used to approve or validate multiple requests
        via Server Action
        """
        queue_id = self.filtered(lambda r: r.status == "new")
        if queue_id:
            for rec in queue_id:
                rec.on_approve()
            message = _("%s request(s) are validated.", len(queue_id))
            kind = "info"
        else:
            message = _("Please select at least 1 new request which need to approve!")
            kind = "warning"
        return self._display_notification(message, kind)

    def generate_validate_requests(self):
        """
        This function is used to generate multiple validated requests
        by creating a Queue Job to work on background
        """
        queue_ids = self.filtered(lambda r: r.status == "approved")
        if queue_ids:
            queue_datas = []
            jobs = []
            max_rec = len(queue_ids)
            for ctr, queued_id in enumerate(queue_ids, 1):
                queued_id.status = "generating"
                message = _("%(user)s started to generate this request on %(date)s.") % {
                    "user": self.env.user.name,
                    "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
                }
                queued_id.save_to_mail_thread(message)
                queue_datas.append(queued_id.id)
                if (ctr % self.JOB_SIZE == 0) or ctr == max_rec:
                    jobs.append(self.delayable()._generate_multi_cards(queue_datas))
                    queue_datas = []
            main_job = group(*jobs)
            main_job.delay()

            message = _("%s request(s) are now being generated.", max_rec)
            kind = "info"
        else:
            message = _("Please select at least 1 approved request which need to generate!")
            kind = "warning"
        return self._display_notification(message, kind)

    def _generate_multi_cards(self, queue_ids):
        queued_ids = self.env["spp.print.queue.id"].search([("id", "in", queue_ids)])
        queued_ids.generate_cards()

    def print_requests(self):
        """
        This function is used to set multiple requests as printed
        """
        queue_id = self.filtered(lambda r: r.status == "generated")
        if queue_id:
            for rec in queue_id:
                rec.on_print()

            message = _("%s request(s) are printed.", len(queue_id))
            kind = "info"
        else:
            message = _("Please select at least 1 generated request which need to print!")
            kind = "warning"
        return self._display_notification(message, kind)

    def distribute_requests(self):
        """
        This function is used to set multiple requests as distributed
        """
        queue_id = self.filtered(lambda r: r.status == "printed")
        if queue_id:
            for rec in queue_id:
                rec.on_distribute()

            message = _("%s request(s) are distributed.", len(queue_id))
            kind = "info"
        else:
            message = _("Please select at least 1 printed request which need to distribute!")
            kind = "warning"
        return self._display_notification(message, kind)

    @api.model
    def _display_notification(self, message, kind):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Requests"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def save_to_mail_thread(self, message):
        for rec in self:
            rec.message_post(body=message)

    def open_request_form(self):
        return {
            "name": "ID Request",
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
            "view_id": self.env.ref("spp_idqueue.view_spp_idqueue_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "flags": {"mode": "readonly"},
        }


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    """
    Add Auto Approve configuration to automatically set
    requests as 'approved' upon creation if auto_approve_id_request
    is True
    """

    auto_approve_id_request = fields.Boolean(
        default=True,
        help="Check if you want to auto-approve ID requests",
        string="Auto-approve ID Requests",
    )

    def set_values(self):
        res = super().set_values()
        self.env["ir.config_parameter"].set_param("spp_id_queue.auto_approve_id_request", self.auto_approve_id_request)
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(auto_approve_id_request=params.get_param("spp_id_queue.auto_approve_id_request"))
        return res
