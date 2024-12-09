# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, models
from odoo.exceptions import UserError

from odoo.addons.g2p_programs.models import constants
from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class DefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def prepare_manual_entitlements(self, cycle, beneficiaries):
        for rec in self:
            rec._ensure_can_edit_cycle(cycle)
            # Get all the enrolled beneficiaries
            beneficiaries_count = len(beneficiaries)
            rec.program_id.get_manager(constants.MANAGER_ENTITLEMENT)
            if beneficiaries_count < self.MIN_ROW_JOB_QUEUE:
                self._prepare_manual_entitlements(cycle, beneficiaries)
            else:
                self._prepare_manual_entitlements_async(cycle, beneficiaries, beneficiaries_count)

    def _prepare_manual_entitlements_async(self, cycle, beneficiaries, beneficiaries_count):
        _logger.debug("Prepare entitlement asynchronously")
        cycle.message_post(body=_("Prepare entitlement for %s beneficiaries started.", beneficiaries_count))
        cycle.write(
            {
                "locked": True,
                "locked_reason": _("Prepare entitlement for beneficiaries."),
            }
        )

        jobs = []
        counter = 1
        beneficiary_vals = []
        for beneficiary in beneficiaries:
            if counter <= self.MAX_ROW_JOB_QUEUE:
                beneficiary_vals.append(beneficiary)
            else:
                counter = 1
                jobs.append(self.delayable()._prepare_manual_entitlements(cycle, beneficiary_vals))
                beneficiary_vals = beneficiary
            counter += 1

        if not jobs:
            jobs.append(self.delayable()._prepare_manual_entitlements(cycle, beneficiary_vals))

        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_prepare_entitlement_as_done(cycle, _("Entitlement Ready.")))
        main_job.delay()

    def _prepare_manual_entitlements(self, cycle, beneficiary_vals):
        ent_manager = self.program_id.get_manager(constants.MANAGER_ENTITLEMENT)
        if not ent_manager:
            raise UserError(_("No Entitlement Manager defined."))
        ent_manager.manual_prepare_entitlements(cycle, beneficiary_vals)
