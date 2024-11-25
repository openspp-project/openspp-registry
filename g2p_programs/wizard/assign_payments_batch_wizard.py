# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class G2PAssignPaymentsBatchWizard(models.TransientModel):
    _name = "g2p.assign.payments.batch.wizard"
    _description = "Add Payments to Batch Wizard"

    cycle_id = fields.Many2one("g2p.cycle", "Cycle", readonly=True)
    internal_batch_ref = fields.Char("Internal Batch Reference #", default=str(uuid4()), readonly=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            # Get the first selected payment and get its cycle_id
            payment_id = self.env.context.get("active_ids")[0]
            payment = self.env["g2p.payment"].search(
                [
                    ("id", "=", payment_id),
                ]
            )
            cycle_id = payment.cycle_id and payment.cycle_id.id or None
            res["cycle_id"] = cycle_id
            return res
        else:
            raise UserError(_("There are no selected payments!"))

    def assign_payment(self):
        if self.env.context.get("active_ids"):
            payment_ids = self.env.context.get("active_ids")
            _logger.info("Assign to Batch Wizard with registrant record IDs: %s" % payment_ids)
            ctr = 0
            ig_ctr = 0
            ok_ctr = 0
            vals = []
            payments_to_add_ids = []
            for rec in self.env["g2p.payment"].search([("id", "in", payment_ids)]):
                ctr += 1
                _logger.info(f"Processing ({ctr}): {rec.name}")
                if not rec.batch_id:
                    ok_ctr += 1
                    vals.append((4, rec.id))
                    payments_to_add_ids.append(rec.id)
                    _logger.info("Adding to Payment Batch: %s" % rec.name)
                else:
                    ig_ctr += 1
                    _logger.info(
                        f"{rec.name} was ignored because the payment is already in Payment Batch:"
                        f"{rec.batch_id.name}"
                    )
            _logger.info(
                f"Total selected payments:{ctr}, Total ignored:{ig_ctr}, Total added to batch:{ok_ctr}"
            )
            # Check if there are no selected payments added to new batch
            if ig_ctr == ctr:
                raise UserError(_("All selected payments are already assigned to another batch."))
            else:
                # Create a new batch
                new_batch_vals = {
                    "name": self.internal_batch_ref,
                    "cycle_id": self.cycle_id.id,
                    "payment_ids": vals,
                    "stats_datetime": fields.Datetime.now(),
                }
                # Add processed payments to new batch
                batch_id = self.env["g2p.payment.batch"].create(new_batch_vals)
                # Update processed payments batch_id
                self.env["g2p.payment"].browse(payments_to_add_ids).update({"batch_id": batch_id})

    def open_wizard(self):
        return {
            "name": "Add to Payment Batch",
            "view_mode": "form",
            "res_model": "g2p.assign.payments.batch.wizard",
            "view_id": self.env.ref("g2p_programs.assign_payments_batch_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }
