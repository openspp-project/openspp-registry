# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.delay import group

from ..programs import G2PProgram

_logger = logging.getLogger(__name__)


class ProgramManager(models.Model):
    _name = "g2p.program.manager"
    _description = "Program Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program", ondelete="cascade")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.manager.default", "Default")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseProgramManager(models.AbstractModel):
    _name = "g2p.base.program.manager"
    _description = "Base Program Manager"

    MIN_ROW_JOB_QUEUE = 200
    MAX_ROW_JOB_QUEUE = 10000

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def last_cycle(self):
        """
        Returns the last cycle of the program
        Returns:
            cycle: the last cycle of the program
        """
        # TODO: implement this
        # sort the program's cycle by sequence and return the last one
        raise NotImplementedError()

    def new_cycle(self):
        """
        Create the next cycle of the program
        Returns:
            cycle: the newly created cycle
        """
        raise NotImplementedError()

    def enroll_eligible_registrants(self, state=None):
        """
        This method is used to enroll the beneficiaries in a program.
        Returns:
            bool: True if the beneficiaries were enrolled, False otherwise.
        """
        raise NotImplementedError()

    def mark_enroll_eligible_as_done(self):
        """Complete the enrollment of eligible beneficiaries.
        Base :meth:`mark_enroll_eligible_as_done`.
        This is executed when all the jobs are completed.
        Post a message in the chatter.
        :return:
        """
        self.ensure_one()
        self.program_id.locked = False
        self.program_id.locked_reason = None
        self.program_id.message_post(body=_("Eligibility check finished."))

        # Compute Statistics
        self.program_id._compute_eligible_beneficiary_count()
        self.program_id._compute_beneficiary_count()


class DefaultProgramManager(models.Model):
    _name = "g2p.program.manager.default"
    _inherit = ["g2p.base.program.manager", "g2p.manager.source.mixin"]
    _description = "Default Program Manager"

    number_of_cycles = fields.Integer(default=1)
    copy_last_cycle_on_new_cycle = fields.Boolean(string="Copy previous cycle", default=True)

    #  TODO: review 'calendar.recurrence' module, it seem the way to go for managing the recurrence
    # recurrence_id = fields.Many2one('calendar.recurrence', related='event_id.recurrence_id')

    def last_cycle(self):
        """
        Returns the last cycle of the program
        Returns:
            cycle: the last cycle of the program
        """
        cycles = self.env["g2p.cycle"].search(
            [("program_id", "=", self.program_id.id)], order="sequence desc", limit=1
        )
        return cycles and cycles[0] or None

    def new_cycle(self):
        """
        Create the next cycle of the program
        Returns:
            cycle: the newly created cycle
        """
        self.ensure_one()

        for rec in self:
            cycles = self.env["g2p.cycle"].search([("program_id", "=", rec.program_id.id)])
            _logger.debug("cycles: %s", cycles)
            cm = rec.program_id.get_manager(G2PProgram.MANAGER_CYCLE)
            if len(cycles) == 0:
                _logger.debug("cycle manager: %s", cm)
                new_cycle = cm.new_cycle("Cycle 1", datetime.now(), 1)
            else:
                last_cycle = rec.last_cycle()
                new_sequence = last_cycle.sequence + 1
                start_date = last_cycle.end_date + timedelta(days=1)
                new_cycle = cm.new_cycle(
                    f"Cycle {new_sequence}",
                    start_date,
                    new_sequence,
                )

            # Copy the enrolled beneficiaries
            if new_cycle is not None:
                program_beneficiaries = rec.program_id.get_beneficiaries("enrolled").mapped("partner_id.id")
                cm.add_beneficiaries(new_cycle, program_beneficiaries, "enrolled")
            return new_cycle

    def enroll_eligible_registrants(self, state=None):
        self.ensure_one()
        # if state is None:
        #    states = ["draft"]
        if isinstance(state, str):
            states = [state]
        else:
            states = state

        program = self.program_id
        members_count = program.get_beneficiaries(state=states, count=True)
        _logger.debug("members: %s", members_count)

        eligibility_managers = program.get_managers(program.MANAGER_ELIGIBILITY)
        if len(eligibility_managers) == 0:
            raise UserError(_("No Eligibility Manager defined."))
        elif members_count < self.MIN_ROW_JOB_QUEUE:
            count = self._enroll_eligible_registrants(state, do_count=True)
            un_enrolled_count = program.get_beneficiaries(state="not_eligible", count=True)
            enrolled_count = program.get_beneficiaries(state="enrolled", count=True)
            if (program.beneficiaries_count == enrolled_count) and not count:
                message = _("No new beneficiaries enrolled.")
            else:
                message = _(
                    f"Enrolled Beneficiaries: {count} successfully and {un_enrolled_count} unsuccessfully."
                )
            kind = "success"
            sticky = False
        else:
            self._enroll_eligible_registrants_async(state, members_count)
            message = _("Eligibility check of %s beneficiaries started.", members_count)
            kind = "warning"
            sticky = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Enrollment"),
                "message": message,
                "sticky": sticky,
                "type": kind,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def _enroll_eligible_registrants_async(self, states, members_count):
        self.ensure_one()
        _logger.debug("members: %s", members_count)
        program = self.program_id
        program.message_post(body=_("Eligibility check of %s beneficiaries started.", members_count))
        program.write({"locked": True, "locked_reason": "Eligibility check of beneficiaries"})

        jobs = []
        for i in range(0, members_count, self.MAX_ROW_JOB_QUEUE):
            jobs.append(
                self.delayable(channel="root_program.program_manager")._enroll_eligible_registrants(
                    states, i, self.MAX_ROW_JOB_QUEUE
                )
            )
        main_job = group(*jobs)
        main_job.on_done(
            self.delayable(channel="root_program.program_manager").mark_enroll_eligible_as_done()
        )
        main_job.delay()

    def _enroll_eligible_registrants(self, states, offset=0, limit=None, do_count=False):
        """Enroll Eligible Registrants

        :param states: List of states to be used in domain filter
        :param offset: Optional integer value for the ORM search offset
        :param limit: Optional integer value for the ORM search limit
        :param do_count: Boolean - set to False to not run compute functions
        :return: Integer - count of not enrolled members
        """
        program = self.program_id
        members = program.get_beneficiaries(state=states, offset=offset, limit=limit, order="id")

        member_before = members

        eligibility_managers = program.get_managers(program.MANAGER_ELIGIBILITY)
        # TODO: Handle multiple eligibility managers properly
        for el in eligibility_managers:
            members = el.enroll_eligible_registrants(members)
        # enroll the one not already enrolled:
        _logger.debug("members filtered: %s", members)
        not_enrolled = members.filtered(lambda m: m.state != "enrolled")
        _logger.debug("not_enrolled: %s", not_enrolled)
        not_enrolled.write(
            {
                "state": "enrolled",
                "enrollment_date": fields.Datetime.now(),
            }
        )
        # dis-enroll the one not eligible anymore:
        enrolled_members_ids = members.ids
        members_to_remove = member_before.filtered(
            lambda m: m.state != "not_eligible" and m.id not in enrolled_members_ids
        )
        # _logger.debug("members_to_remove: %s", members_to_remove)
        members_to_remove.write(
            {
                "state": "not_eligible",
            }
        )

        if do_count:
            # Compute Statistics
            program._compute_eligible_beneficiary_count()
            program._compute_beneficiary_count()

        return len(not_enrolled)
