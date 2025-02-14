# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPRequestIDWizard(models.TransientModel):
    _name = "spp.print.queue.wizard"
    _description = "Request ID Wizard"

    registrant_id = fields.Many2one("res.partner", "Registrant ID", required=True)
    id_type = fields.Many2one("g2p.id.type")
    is_idpass = fields.Boolean(default=False)
    idpass_id = fields.Many2one("spp.id.pass", "IDPass ID")
    target_type = fields.Char(compute="_compute_target_type")

    @api.depends("registrant_id")
    def _compute_target_type(self):
        """
        This function is used to compute target_type
        """
        for rec in self:
            if rec.registrant_id:
                if rec.registrant_id.is_group:
                    rec.target_type = "group"
                else:
                    rec.target_type = "individual"

    def request_id(self):
        """
        This function is used to create the request
        """
        for rec in self:
            if rec.id_type:
                params = self.env["ir.config_parameter"].sudo()
                auto_approve_id_request = params.get_param("spp_id_queue.auto_approve_id_request")
                status = "new"
                if auto_approve_id_request:
                    status = "approved"
                vals = {
                    "id_type": rec.id_type.id,
                    "idpass_id": rec.idpass_id.id or False,
                    "requested_by": self.env.user.id,
                    "date_requested": date.today(),
                    "status": status,
                    "registrant_id": rec.registrant_id.id,
                }
                return self.env["spp.print.queue.id"].create(vals)
            else:
                raise UserError(_("There are no selected Template!"))

    @api.onchange("id_type")
    def _onchange_template(self):
        """
        This function is used to set is_idpass on Template onchange
        """
        for rec in self:
            rec.is_idpass = False
            _logger.info("ID REQUEST: {} {}".format(rec.id_type.id, self.env.ref("spp_idpass.id_type_idpass").id))
            if rec.id_type and rec.id_type.id == self.env.ref("spp_idpass.id_type_idpass").id:
                rec.is_idpass = True
