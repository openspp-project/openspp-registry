# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models

from odoo.addons.queue_job.delay import group

_logger = logging.getLogger(__name__)


class EligibilityManager(models.Model):
    _name = "g2p.eligibility.manager"
    _description = "Eligibility Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program", ondelete="cascade")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program_membership.manager.default", "Default Eligibility")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseEligibilityManager(models.AbstractModel):
    _name = "g2p.program_membership.manager"
    _inherit = "base.programs.manager"
    _description = "Base Eligibility"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def enroll_eligible_registrants(self, program_memberships):
        """
        This method is used to validate if a user match the criteria needed to be enrolled in a program.
        Args:
            program_membership:

        Returns:
            bool: True if the user match the criterias, False otherwise.
        """
        raise NotImplementedError()

    def verify_cycle_eligibility(self, cycle, membership):
        """
        This method is used to validate if a beneficiary match the criteria needed to be enrolled in a cycle.
        Args:
            cycle:
            membership:

        Returns:
            bool: True if the cycle match the criterias, False otherwise.
        """
        raise NotImplementedError()

    def import_eligible_registrants(self, state=None):
        """
        This method is used to import the beneficiaries in a program.
        Returns:
        """
        raise NotImplementedError()


class DefaultEligibilityManager(models.Model):
    _name = "g2p.program_membership.manager.default"
    _inherit = ["g2p.program_membership.manager", "g2p.manager.source.mixin"]
    _description = "Simple Eligibility"

    # TODO: rename to allow_
    # support_individual = fields.Boolean(string="Support Individual", default=False)
    # support_group = fields.Boolean(string="Support Group", default=False)

    # TODO: cache the parsed domain
    eligibility_domain = fields.Text(string="Domain", default="[]")

    def _prepare_eligible_domain(self, membership=None):
        domain = []
        if membership is not None:
            ids = membership.mapped("partner_id.id")
            domain += [("id", "in", ids)]

        # Do not include disabled registrants
        domain += [("disabled", "=", False)]
        # TODO: use the config of the program
        if self.program_id.target_type == "group":
            domain += [("is_group", "=", True), ("is_registrant", "=", True)]
        if self.program_id.target_type == "individual":
            domain += [("is_group", "=", False), ("is_registrant", "=", True)]
        domain += self._safe_eval(self.eligibility_domain)
        # _logger.debug("DOMAIN: %s" % domain)
        return domain

    def enroll_eligible_registrants(self, program_memberships):
        # TODO: check if the beneficiary still match the criterias
        _logger.debug("-" * 100)
        _logger.debug("Checking eligibility for %s", program_memberships)
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
        domain = self._prepare_eligible_domain(membership)
        _logger.debug("Eligibility domain: %s", domain)
        beneficiaries = self.env["res.partner"].search(domain).ids
        _logger.debug("Beneficiaries: %s", beneficiaries)
        return beneficiaries

    def import_eligible_registrants(self, state="draft"):
        # TODO: this only take the first eligibility manager, no the others
        # TODO: move this code to the program manager and use the eligibility manager
        #  like done for enroll_eligible_registrants

        for rec in self:
            domain = rec._prepare_eligible_domain()
            new_beneficiaries = self.env["res.partner"].search(domain)
            # logging.debug("Found %s beneficiaries", len(new_beneficiaries))

            # Exclude already added beneficiaries
            beneficiary_ids = rec.program_id.get_beneficiaries().mapped("partner_id")

            # logging.debug("Excluding %s beneficiaries", len(beneficiary_ids))
            new_beneficiaries = new_beneficiaries - beneficiary_ids
            # logging.debug("Finally %s beneficiaries", len(new_beneficiaries))

            if len(new_beneficiaries) < 1000:
                rec._import_registrants(new_beneficiaries, state=state, do_count=True)
            else:
                rec._import_registrants_async(new_beneficiaries, state=state)

    def _import_registrants_async(self, new_beneficiaries, state="draft"):
        self.ensure_one()
        program = self.program_id
        program.message_post(body="Import of %s beneficiaries started." % len(new_beneficiaries))
        program.write({"locked": True, "locked_reason": "Importing beneficiaries"})

        jobs = []
        for i in range(0, len(new_beneficiaries), 10000):
            jobs.append(
                self.delayable(channel="root_program.eligibility_manager")._import_registrants(
                    new_beneficiaries[i : i + 10000], state
                )
            )
        main_job = group(*jobs)
        main_job.on_done(self.delayable(channel="root_program.eligibility_manager").mark_import_as_done())
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
