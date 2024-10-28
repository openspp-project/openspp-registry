# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import math

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPBatchCreateWizard(models.TransientModel):
    _name = "spp.batch.create.wizard"
    _description = "Create Batch Wizard"

    @api.model
    def default_get(self, fields):
        """
        Default Get
        These overrides the default_get function to set the
        queue_ids, state and id_count depending on different
        scenarios
        """
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            queue_id = self.env["spp.print.queue.id"].search(
                [
                    ("id", "in", self.env.context.get("active_ids")),
                    ("status", "=", "approved"),
                    ("batch_id", "=", False),
                ]
            )

            if len(queue_id) > 0:
                id_types = queue_id.mapped("id_type.id")
                templates = queue_id.mapped("idpass_id.id")
                if len(set(templates)) > 1 or len(set(id_types)) > 1:
                    res["queue_ids"] = queue_id
                    res["state"] = "step1"
                else:
                    res["queue_ids"] = queue_id
                    res["id_count"] = len(queue_id)
                    res["id_type"] = id_types[0]
                    res["state"] = "step2"
            else:
                raise UserError(_("No approved id requests selected!"))
            return res
        else:
            raise UserError(_("There are no selected id requests!"))

    name = fields.Char(string="Batch Name")
    id_count = fields.Integer(string="ID Count")
    max_id_per_batch = fields.Integer(string="Max ID per batch", default=20)
    batches_count = fields.Integer(string="Batches to be created", compute="_compute_batches_count")
    queue_ids = fields.Many2many("spp.print.queue.id")
    id_type = fields.Many2one("g2p.id.type", required=True, string="ID Type")
    idpass_id = fields.Many2one("spp.id.pass", string="Template", domain="[('id_type', '=', id_type)]")
    state = fields.Selection(
        [("step1", "Set Template"), ("step2", "Set Batch")],
        "Status",
        default="step1",
        readonly=True,
    )

    def next_step(self):
        """
        This function is used to proceed to 2nd Step which are
        the batch creation
        """
        for rec in self:
            if rec.queue_ids and (rec.idpass_id or rec.id_type):
                domain = [("id", "in", rec.queue_ids.ids)]
                if rec.idpass_id:
                    domain.append(("idpass_id", "=", rec.idpass_id.id))
                if rec.id_type:
                    domain.append(("id_type", "=", rec.id_type.id))
                queue_id = self.env["spp.print.queue.id"].search(domain)
                if queue_id:
                    rec.queue_ids = queue_id
                    rec.id_count = len(queue_id)
                    rec.state = "step2"
                return self._reopen_self()

    def create_batch(self):
        """
        This function is used to create the batch or batches
        """
        for rec in self:
            id_count = 0
            batches_count = rec.batches_count
            batch_name = rec.name
            if batches_count > 1:
                batch_name = _("%s - 1", rec.name)
            batch_id = self.env["spp.print.queue.batch"].create({"name": batch_name})
            current_batch_count = 1
            queue_ids = []
            for queue in rec.queue_ids:
                if not current_batch_count > batches_count:
                    id_count += 1
                    if not id_count > rec.max_id_per_batch:
                        queue_ids.append([4, queue.id])
                    else:
                        batch_id.write({"queued_ids": queue_ids})
                        queue_ids = []
                        if not current_batch_count == batches_count:
                            batch_name = f"{rec.name or ''} - {current_batch_count + 1}"
                            batch_id = self.env["spp.print.queue.batch"].create({"name": batch_name})
                            queue_ids.append([4, queue.id])
                            id_count = 1
                            current_batch_count += 1

            # Write the last batch
            if queue_ids:
                batch_id.write({"queued_ids": queue_ids})

            message = _("%s batch(es) created.", rec.batches_count)
            kind = "info"
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

    @api.depends("max_id_per_batch", "id_count")
    def _compute_batches_count(self):
        """
        This function is used to compute the count of batches to be created
        """
        for rec in self:
            rec.batches_count = 1
            if rec.max_id_per_batch and rec.id_count:
                if rec.max_id_per_batch > rec.id_count:
                    rec.batches_count = 1
                else:
                    rec.batches_count = math.ceil(rec.id_count / rec.max_id_per_batch)

    def open_wizard(self):
        return {
            "name": "Create Batch Printing",
            "view_mode": "form",
            "res_model": "spp.batch.create.wizard",
            "view_id": self.env.ref("spp_idqueue.batch_create_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
