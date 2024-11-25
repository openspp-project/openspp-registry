# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

from odoo.addons.calendar.models import calendar_recurrence


class RecurrenceMixin(models.Model):
    """Cycle Recurrence mixin."""

    _name = "g2p.cycle.recurrence.mixin"
    _description = "Cycle Recurrence Mixin"
    _inherit = "calendar.recurrence"

    # Overwrite field to add readonly to False
    name = fields.Char(required=True, readonly=False)

    # Overwrite field from calendar.recurrence to define string and re-define default value
    rrule_type = fields.Selection(
        calendar_recurrence.RRULE_TYPE_SELECTION,
        string="Recurrence",
        default="monthly",
        help="Let the event automatically repeat at that interval",
        readonly=False,
        required=True,
    )

    # Overwrite field from calendar.recurrence to define default value
    byday = fields.Selection(calendar_recurrence.BYDAY_SELECTION, string="By day", default="1")

    # Overwrite field from calendar.recurrence to define default value
    count = fields.Integer(default=10)

    # Overwrite field from calendar.recurrence to add compute argument,
    #  store = True, and re-define default value
    interval = fields.Integer(default=1, compute="_compute_interval", store=True)

    # Overwrite to always return False
    def _is_allday(self):
        return False

    def _get_recurrent_field_values(self):
        for rec in self:
            return {
                "byday": rec.byday,
                "until": rec.until,
                "rrule_type": rec.rrule_type,
                "month_by": rec.month_by,
                "event_tz": rec.event_tz,
                "rrule": rec.rrule,
                "interval": rec.interval,
                "count": rec.count,
                "end_type": rec.end_type,
                "mon": rec.mon,
                "tue": rec.tue,
                "wed": rec.wed,
                "thu": rec.thu,
                "fri": rec.fri,
                "sat": rec.sat,
                "sun": rec.sun,
                "day": rec.day,
                "weekday": rec.weekday,
            }

    def _compute_interval(self):
        """
        Copy value of a field to interval
        """
        raise NotImplementedError()

    def _compute_name(self):
        # Overwrite this function of calendar.recurrence to do nothing
        pass

    def _inverse_rrule(self):
        # Overwrite this function of calendar.recurrence to do nothing
        pass
