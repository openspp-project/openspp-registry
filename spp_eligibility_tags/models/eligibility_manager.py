# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import _, api, fields, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class EligibilityManager(models.Model):
    _inherit = "g2p.eligibility.manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program_membership.manager.tags", "Tag-based Eligibility")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class TagBasedEligibilityManager(models.Model):
    _name = "g2p.program_membership.manager.tags"
    _inherit = ["g2p.program_membership.manager", "g2p.manager.source.mixin"]
    _description = "Tag-based Eligibility"

    tags_id = fields.Many2one("g2p.registrant.tags", string="Tags")
    area_id = fields.Many2one(
        "spp.area",
        domain=lambda self: [("kind", "=", self.env.ref("spp_area_base.admin_area_kind").id)],
    )

    custom_domain = fields.Text(string="Tags Domain", default="[]", readonly=True, compute="_compute_custom_domain")

    target_type = fields.Selection(related="program_id.target_type")

    NON_ASYNC_LIMIT = 1000
    MAX_ROW_JOB_QUEUE = 10000

    def _compute_custom_domain(self):
        domain = self._get_beneficiaries_by_tags()
        self.custom_domain = json.dumps(domain)

    def _prepare_eligible_domain(self, membership=None):
        domain = []

        domain.extend(self._get_initial_domain(membership=membership))
        domain.extend(self._get_beneficiaries_by_tags())

        return domain

    def _get_initial_domain(self, membership=None):
        domain = []

        if membership:
            ids = membership.mapped("partner_id.id")
            if ids:
                domain.append(("id", "in", ids))

        # Do not include disabled registrants
        domain.append(("disabled", "=", False))
        if self.program_id.target_type == "group":
            domain.append(("is_group", "=", True))
        if self.program_id.target_type == "individual":
            domain.append(("is_group", "=", False))

        return domain

    def _get_beneficiaries_by_tags(self):
        domain = []

        if self.tags_id:
            domain.append(("tags_ids", "=", self.tags_id.id))

        if self.area_id:
            domain.append(("area_id", "=", self.area_id.id))

        return domain

    def enroll_eligible_registrants(self, program_memberships):
        for rec in self:
            beneficiaries = rec._verify_eligibility(program_memberships)
            return self.env["g2p.program_membership"].search(
                [
                    ("partner_id", "in", beneficiaries),
                    ("program_id", "=", self.program_id.id),
                ]
            )

    def verify_cycle_eligibility(self, cycle, membership):
        for rec in self:
            beneficiaries = rec._verify_eligibility(membership)
            return self.env["g2p.cycle.membership"].search([("partner_id", "in", beneficiaries)])

    def _verify_eligibility(self, membership):
        domain = self._prepare_eligible_domain(membership=membership)
        beneficiaries = self.env["res.partner"].search(domain).ids
        return beneficiaries

    def import_eligible_registrants(self, state="draft"):
        for rec in self:
            domain = rec._prepare_eligible_domain()
            new_beneficiaries = self.env["res.partner"].search(domain)

            # Exclude already added beneficiaries
            beneficiary_ids = rec.program_id.get_beneficiaries().mapped("partner_id")
            new_beneficiaries = new_beneficiaries - beneficiary_ids

            new_beneficiaries_count = len(new_beneficiaries)

            if len(new_beneficiaries) < self.NON_ASYNC_LIMIT:
                rec._import_registrants(new_beneficiaries, state=state, do_count=True)
            else:
                rec._import_registrants_async(new_beneficiaries, state=state)

            return new_beneficiaries_count

    def _import_registrants_async(self, new_beneficiaries, state="draft"):
        self.ensure_one()
        program = self.program_id
        program.message_post(body="Import of %s beneficiaries started." % len(new_beneficiaries))
        program.write({"locked": True, "locked_reason": "Importing beneficiaries"})

        jobs = []
        for i in range(0, len(new_beneficiaries), self.MAX_ROW_JOB_QUEUE):
            jobs.append(self.delayable()._import_registrants(new_beneficiaries[i : i + self.MAX_ROW_JOB_QUEUE], state))
        main_job = group(*jobs)
        main_job.on_done(self.delayable().mark_import_as_done())
        main_job.delay()

    def mark_import_as_done(self):
        self.ensure_one()
        self.program_id._compute_eligible_beneficiary_count()
        self.program_id._compute_beneficiary_count()

        self.program_id.locked = False
        self.program_id.locked_reason = None
        self.program_id.message_post(body=_("Import finished."))

    def _import_registrants(self, new_beneficiaries, state="draft", do_count=False):
        logging.info("Importing %s beneficiaries", len(new_beneficiaries))
        logging.info("updated")
        beneficiaries_val = []
        for beneficiary in new_beneficiaries:
            beneficiaries_val.append((0, 0, {"partner_id": beneficiary.id, "state": state}))
        self.program_id.update({"program_membership_ids": beneficiaries_val})

        if do_count:
            # Compute Statistics
            self.program_id._compute_eligible_beneficiary_count()
            self.program_id._compute_beneficiary_count()
