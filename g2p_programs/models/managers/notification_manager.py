# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class Notification(models.Model):
    _name = "g2p.program.notification.manager"
    _description = "Program Notification Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program", ondelete="cascade")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.notification.manager.sms", "SMS Notification")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseNotificationManager(models.AbstractModel):
    """
    This component is used to notify beneficiaries of their enrollment and other events related to the program
    """

    _name = "g2p.base.program.notification.manager"
    _description = "Base Program Notification Manager"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)
    on_enrolled_in_program = fields.Boolean(default=True)
    on_cycle_started = fields.Boolean(default=True)
    on_cycle_ended = fields.Boolean(default=True)

    def on_enrolled_in_program(self, program_memberships):
        return

    def on_cycle_started(self, program_memberships, cycle):
        return

    def on_cycle_ended(self, program_memberships, cycle):
        return


class SMSNotificationManager(models.Model):
    _name = "g2p.program.notification.manager.sms"
    _inherit = ["g2p.base.program.notification.manager", "g2p.manager.source.mixin"]
    _description = "SMS Program Notification Manager"

    on_enrolled_in_program_template = fields.One2many("sms.template", "g2p_sms_id")
    on_cycle_started_template = fields.One2many("sms.template", "g2p_sms_id")
    on_cycle_ended_template = fields.One2many("sms.template", "g2p_sms_id")

    # TODO: render the templates and send the sms using a job
    def on_enrolled_in_program(self, program_memberships):
        return

    def on_cycle_started(self, program_memberships, cycle):
        return

    def on_cycle_ended(self, program_memberships, cycle):
        return


class SMSTemplate(models.Model):
    _inherit = "sms.template"

    g2p_sms_id = fields.Many2one("g2p.program.notification.manager.sms", "SMS Program Notification Manager")
