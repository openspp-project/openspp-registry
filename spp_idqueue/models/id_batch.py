# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


import json
from datetime import date, datetime

import requests

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group


class OpenSPPPrintBatch(models.Model):
    _name = "spp.print.queue.batch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ID print Batch"
    _order = "id DESC"

    JOBBATCH_SIZE = 20

    name = fields.Char("Batch name")

    #  We should only allow `approved` id to be added to a batch
    queued_ids = fields.One2many("spp.print.queue.id", "batch_id", string="Queued IDs")
    status = fields.Selection(
        [
            ("new", "New"),
            ("approved", "Approved"),
            ("generating", "Generating"),
            ("generated", "Generated"),
            ("printing", "Printing"),
            ("printed", "Printed"),
            ("distributed", "Distributed"),
        ],
        default="new",
    )

    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")
    merge_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("merged", "Merged"),
            ("error_sending", "Error Sending"),
            ("error_merging", "Error Merging"),
        ],
        default="draft",
    )
    approved_by = fields.Many2one("res.users")
    printed_by = fields.Many2one("res.users")
    distributed_by = fields.Many2one("res.users")
    date_approved = fields.Date()
    date_printed = fields.Date()
    date_distributed = fields.Date()
    date_merged = fields.Date()

    def refresh_data(self):
        return

    def approve_batch(self):
        """
        This function is used to approve or validate a batch
        """
        for rec in self:
            rec.date_approved = date.today()
            rec.approved_by = self.env.user.id
            rec.status = "approved"
            message = _("%(user)s validated this batch on %(date)s.") % {
                "user": rec.approved_by.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)

    def generate_batch(self):
        return self._generate_batch(self)

    def _generate_batch(self, batch_ids):
        """
        This function is used to generate cards from batch by
        creating a Queue Job for each Job Batch
        :param batch_ids: The Batch IDS.
        :return: Return a notification to state the progress
        """
        ctr_batch = 0
        ctr_ids = 0
        for rec in batch_ids:
            ctr_batch += 1
            rec.status = "generating"
            queued_ids = []
            jobs = []
            max_rec = len(rec.queued_ids)
            for ctr, queued_id in enumerate(rec.queued_ids, 1):
                queued_id.status = "generating"
                message = _("%(user)s started to generate this request on %(date)s.") % {
                    "user": self.env.user.name,
                    "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
                }
                queued_id.save_to_mail_thread(message)
                ctr_ids += 1
                queued_ids.append(queued_id.id)
                if (ctr % self.JOBBATCH_SIZE == 0) or ctr == max_rec:
                    jobs.append(rec.delayable(channel="root_id_batch.id_batch")._generate_cards(queued_ids))
                    queued_ids = []

            main_job = group(*jobs)
            main_job.on_done(self.delayable(channel="root_id_batch.id_batch").mark_as_done(rec))
            main_job.delay()

            message_1 = _("%(user)s started to generate this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message_1)

        message = _("%(batch_count)s Batch(es) with total of %(id_count)s IDs are being generated.") % {
            "batch_count": ctr_batch or "",
            "id_count": ctr_ids or "",
        }
        kind = "info"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def _generate_cards(self, queue_ids):
        """
        This generates each cards from the Batch via Queue Jobs
        :param queued_ids: The Queue IDS.
        :return: Call generate_cards
        """
        queued_ids = self.env["spp.print.queue.id"].search([("id", "in", queue_ids)])
        queued_ids.generate_cards()

    def mark_as_done(self, rec):
        """
        This function is used to set the batch as 'generated' when the
        Queue Job is Done
        :param rec: The Record.
        :return: Set status, call save_to_mail_thread then pass the api parameter
        """
        if not rec.queued_ids.filtered(lambda x: x.status != "generated"):
            rec.status = "generated"
            message = _("%(user)s generated this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)
            rec.pass_api_param()
        else:
            raise ValidationError(_("Some IDs are not generated"))

    def retry_pass_api(self):
        for rec in self:
            rec.pass_api_param()

    def pass_api_param(self):
        """
        This function is used to pass the Batch ID on API
        to merge all Individual IDS to one PDF
        """
        for rec in self:
            batch_param = self.env["spp.id.pass"].search(
                [("id", "=", self.env.ref("spp_idqueue.id_template_batch_print").id)]
            )
            if batch_param and batch_param.auth_token and batch_param.api_url:
                token = _("Token %s", batch_param.auth_token)
                data = {
                    "batch_id": str(rec.id),
                }
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": token,
                }

                response = requests.post(
                    batch_param.api_url,
                    data=json.dumps(data),
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    rec.merge_status = "sent"
                else:
                    rec.merge_status = "error_sending"
            else:
                message = _("No Auth Token or API URL")
                raise ValidationError(message)
        return

    def print_batch(self):
        """
        This function is used to set the Batch to 'printing'
        """
        for rec in self:
            rec.status = "printing"
            message = _("%(user)s started to print this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)
            for queue_id in rec.queued_ids:
                message = _("%(user)s started to print this request on %(date)s.") % {
                    "user": self.env.user.name,
                    "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
                }
                queue_id.save_to_mail_thread(message)

    def batch_printed(self):
        """
        This function is used to set the Batch and each individual IDs
        to 'printed'
        """
        for rec in self:
            rec.date_printed = date.today()
            rec.printed_by = self.env.user.id
            rec.status = "printed"

            for queue_id in rec.queued_ids:
                queue_id.date_printed = date.today()
                queue_id.printed_by = self.env.user.id
                queue_id.status = "printed"
                message = _("%(user)s printed this request on %(date)s.") % {
                    "user": self.env.user.name,
                    "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
                }
                queue_id.save_to_mail_thread(message)

            message = _("%(user)s printed this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)

    def batch_distributed(self):
        """
        This function is used to set the Batch and each individual IDs
        to 'distributed'
        """
        for rec in self:
            rec.date_distributed = date.today()
            rec.distributed_by = self.env.user.id
            rec.status = "distributed"

            for queue_id in rec.queued_ids:
                queue_id.date_distributed = date.today()
                queue_id.status = "distributed"
                message = _("%(user)s distributed this request on %(date)s.") % {
                    "user": self.env.user.name,
                    "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
                }
                queue_id.save_to_mail_thread(message)

            message = _("%(user)s distributed this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            rec.save_to_mail_thread(message)

    def multi_approve_batch(self):
        """
        This function is used for server action to approve multi-selected batches
        """
        batch_ids = self.filtered(lambda r: r.status == "new")
        if batch_ids:
            max_rec = len(batch_ids)
            batch_ids.write(
                {
                    "date_approved": fields.Date.today(),
                    "approved_by": self.env.user.id,
                    "status": "approved",
                }
            )
            message = _("%(user)s validated this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.save_to_mail_thread(message)

            message = _("%s batch(es) are validated.", max_rec)
            kind = "info"
        else:
            message = _("Please select at least 1 new batch need to approve!")
            kind = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def multi_generate_batch(self):
        """
        This function is used for server action to generate multi-selected batches
        """
        batch_ids = self.filtered(lambda r: r.status == "approved")
        if batch_ids:
            return self._generate_batch(batch_ids)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
                "message": _("Please select at least 1 approved batch need to approve!"),
                "sticky": True,
                "type": "warning",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def multi_print_batch(self):
        """
        This function is used for server action to print multi-selected batches
        """
        batch_ids = self.filtered(lambda r: r.status == "generated" and r.merge_status == "merged")
        if batch_ids:
            max_rec = len(batch_ids)
            batch_ids.write({"status": "printing"})
            message = _("%(user)s started to print this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.save_to_mail_thread(message)
            message = _("%(user)s started to print this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.queued_ids.save_to_mail_thread(message)

            message = _("%s batch(es) are being printed.", max_rec)
            kind = "info"
        else:
            message = _("Please select at least 1 generated batch need to print!")
            kind = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def multi_printed_batch(self):
        """
        This function is used for server action to set multi-selected batches and
        their Individual IDs as printed
        """
        batch_ids = self.filtered(lambda r: r.status == "printing")
        if batch_ids:
            max_rec = len(batch_ids)
            batch_ids.write(
                {
                    "date_printed": fields.Date.today(),
                    "printed_by": self.env.user.id,
                    "status": "printed",
                }
            )
            message = _("%(user)s printed this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.save_to_mail_thread(message)
            batch_ids.queued_ids.write(
                {
                    "date_printed": fields.Date.today(),
                    "printed_by": self.env.user.id,
                    "status": "printed",
                }
            )
            message = _("%(user)s printed this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.queued_ids.save_to_mail_thread(message)

            message = _("%s batch(es) are printed.", max_rec)
            kind = "info"
        else:
            message = _("Please select at least 1 printing batch need to printed!")
            kind = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
                "message": message,
                "sticky": True,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def multi_distribute_batch(self):
        """
        This function is used for server action to set multi-selected batches and
        their Individual IDs as distributed
        """
        batch_ids = self.filtered(lambda r: r.status == "printed")
        if batch_ids:
            max_rec = len(batch_ids)
            batch_ids.write(
                {
                    "date_distributed": fields.Date.today(),
                    "distributed_by": self.env.user.id,
                    "status": "distributed",
                }
            )
            message = _("%(user)s distributed this batch on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.save_to_mail_thread(message)
            batch_ids.queued_ids.write(
                {
                    "date_distributed": fields.Date.today(),
                    "status": "distributed",
                }
            )
            message = _("%(user)s distributed this request on %(date)s.") % {
                "user": self.env.user.name,
                "date": datetime.now().strftime("%B %d, %Y at %H:%M"),
            }
            batch_ids.queued_ids.save_to_mail_thread(message)

            message = _("%s batch(es) are distributed.", max_rec)
            kind = "info"
        else:
            message = _("Please select at least 1 printed batch need to distribute!")
            kind = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("ID Batch"),
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
