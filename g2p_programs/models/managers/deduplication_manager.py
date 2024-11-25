# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import collections
import itertools
import logging
from datetime import date

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DeduplicationManager(models.Model):
    _name = "g2p.deduplication.manager"
    _description = "Deduplication Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program", ondelete="cascade")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_managers = [
            ("g2p.deduplication.manager.default", "Default Deduplication"),
            ("g2p.deduplication.manager.phone_number", "Phone Number Deduplication"),
            ("g2p.deduplication.manager.id_dedup", "ID Deduplication"),
        ]
        for new_manager in new_managers:
            if new_manager not in selection:
                selection.append(new_manager)
        return selection


class BaseDeduplication(models.AbstractModel):
    _name = "g2p.base.deduplication.manager"
    _description = "Base Deduplication Manager"

    # Kind of deduplication possible
    _capability_individual = False
    _capability_group = False

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def deduplicate_beneficiaries(self, states):
        raise NotImplementedError()


class DefaultDeduplication(models.Model):
    _name = "g2p.deduplication.manager.default"
    _inherit = ["g2p.base.deduplication.manager", "g2p.manager.source.mixin"]
    _description = "Default Deduplication Manager"

    _capability_individual = True
    _capability_group = True

    def deduplicate_beneficiaries(self, states):
        for rec in self:
            duplicate_beneficiaries = []
            program = rec.program_id
            beneficiaries = program.get_beneficiaries(states)
            # duplicates
            _logger.debug("Deduplicate beneficiaries: %s", beneficiaries)
            if program.target_type == "group":
                duplicate_beneficiaries = self._check_duplicate_by_individual_ids(beneficiaries)
            return len(duplicate_beneficiaries)

    def _record_duplicate(self, manager, beneficiary_ids, reason):
        """
        This method is used to record a duplicate beneficiary.
        :param beneficiary: The beneficiary.
        :param reason: The reason.
        :param comment: The comment.
        :return:
        """

        # TODO: check this group does not exist already with the same manager and the same beneficiaries or
        #  a subset of them.
        #  1. If the state has been changed to no_duplicate,
        # then we should not record it as duplicate unless there are
        #  additional beneficiaries in the group.
        #  2. Otherwise we update the record.

        _logger.debug("Record duplicate: %s", beneficiary_ids)

        existing_record = self.env["g2p.program.membership.duplicate"].search(
            [
                ("beneficiary_ids", "in", beneficiary_ids),
                ("state", "=", "duplicate"),
                ("deduplication_manager_id", "=", manager.id),
                ("reason", "=", reason),
            ]
        )
        if not existing_record:
            data = {
                "beneficiary_ids": [(6, 0, beneficiary_ids)],
                "state": "duplicate",
                "reason": reason,
                "deduplication_manager_id": manager,
            }
            _logger.debug("Record duplicate: %s", data)

            self.env["g2p.program.membership.duplicate"].create(data)

    def _check_duplicate_by_individual_ids(self, beneficiaries):
        """
        This method is used to check if there are any duplicates among the individuals.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.debug("-" * 100)
        group_ids = beneficiaries.mapped("partner_id.id")
        group_memberships = self.env["g2p.group.membership"].search([("group", "in", group_ids)])
        _logger.debug("group_memberships: %s", group_memberships)

        individuals_ids = [rec.individual.id for rec in group_memberships]
        _logger.debug("individuals_ids: %s", individuals_ids)

        duplicate_individuals = [
            item for item, count in collections.Counter(individuals_ids).items() if count > 1
        ]
        _logger.debug("Duplicate individuals: %s", duplicate_individuals)

        group_with_duplicates = self.env["g2p.group.membership"].search(
            [("group", "in", group_ids), ("individual", "in", duplicate_individuals)]
        )

        _logger.debug("group_with_duplicates: %s", group_with_duplicates)
        group_of_duplicates = {}
        for group_membership in group_with_duplicates:
            _logger.debug(
                f"group_membership.individual.id: {group_membership.individual.id} -> "
                f"{group_membership.group.id}"
            )
            if group_membership.individual.id not in group_of_duplicates:
                group_of_duplicates[group_membership.individual.id] = []
            group_of_duplicates[group_membership.individual.id].append(group_membership.group.id)

        _logger.debug("group_of_duplicates: %s", group_of_duplicates)
        for _individual, group_ids in group_of_duplicates.items():
            duplicate_beneficiaries = beneficiaries.filtered(lambda rec: rec.partner_id.id in group_ids)
            duplicate_beneficiariy_ids = duplicate_beneficiaries.mapped("id")

            self._record_duplicate(self, duplicate_beneficiariy_ids, "Duplicate individuals")

            duplicated_enrolled = duplicate_beneficiaries.filtered(lambda rec: rec.state == "enrolled")
            if len(duplicated_enrolled) == 1:
                # If there is only 1 enrolled that is duplicated,
                # the enrolled one should not be marked as duplicate.
                # otherwise if there is more than 1, then there is a problem!
                # TODO: check how to handle this
                duplicated_enrolled.write({"state": "enrolled"})
                duplicate_beneficiaries = duplicate_beneficiaries.filtered(
                    lambda rec: rec.state != "enrolled"
                )
            duplicate_beneficiaries.filtered(
                lambda rec: rec.state not in ["exited", "not_eligible", "duplicated"]
            ).write({"state": "duplicated"})

        return group_with_duplicates


class IDDocumentDeduplication(models.Model):
    _name = "g2p.deduplication.manager.id_dedup"
    _inherit = ["g2p.base.deduplication.manager", "g2p.manager.source.mixin"]
    _description = "ID Deduplication Manager"

    supported_id_document_types = fields.Many2many("g2p.id.type", string="Supported ID Document Types")

    def deduplicate_beneficiaries(self, states):
        for rec in self:
            duplicate_beneficiaries = []
            program = rec.program_id
            beneficiaries = program.get_beneficiaries(states)
            # duplicates
            _logger.debug("Deduplicate beneficiaries: %s", beneficiaries)
            if program.target_type == "group":
                duplicate_beneficiaries = self._check_duplicate_by_group_with_individual(beneficiaries)
            else:
                duplicate_beneficiaries = self._check_duplicate_by_individual(beneficiaries)
            return len(duplicate_beneficiaries)

    def _record_duplicate(self, manager, beneficiary_ids, reason):
        """
        This method is used to record a duplicate beneficiary.
        :param beneficiary: The beneficiary.
        :param reason: The reason.
        :param comment: The comment.
        :return:
        """

        # TODO: check this group does not exist already with the same manager
        # and the same beneficiaries or
        #  a subset of them.
        #  1. If the state has been changed to no_duplicate, then
        #  we should not record it as duplicate unless there are
        #  additional beneficiaries in the group.
        #  2. Otherwise we update the record.

        _logger.debug("Record duplicate: %s", beneficiary_ids)

        existing_record = self.env["g2p.program.membership.duplicate"].search(
            [
                ("beneficiary_ids", "in", beneficiary_ids),
                ("state", "=", "duplicate"),
                ("deduplication_manager_id", "=", manager.id),
                ("reason", "=", reason),
            ]
        )
        if not existing_record:
            data = {
                "beneficiary_ids": [(6, 0, beneficiary_ids)],
                "state": "duplicate",
                "reason": reason,
                "deduplication_manager_id": manager,
            }
            _logger.debug("Record duplicate: %s", data)

            self.env["g2p.program.membership.duplicate"].create(data)

    def _check_duplicate_by_group_with_individual(self, beneficiaries):
        """
        This method is used to check if there are any duplicates among the individuals docs.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.debug("-" * 100)
        group_ids = beneficiaries.mapped("partner_id.id")
        group_memberships = self.env["g2p.group.membership"].search([("group", "in", group_ids)])
        group = self.env["res.partner"].search([("id", "in", group_ids)])
        _logger.debug("group_memberships: %s", group_memberships)

        individuals_ids = [rec.individual.id for rec in group_memberships]
        _logger.debug("Checking ID Document Duplicates for: %s", individuals_ids)

        individual_id_docs = {}
        # Check ID Documents of each individual
        for i in group_memberships:
            for x in i.individual.reg_ids:
                if x.id_type in self.supported_id_document_types and (
                    (not x.expiry_date) or x.expiry_date > date.today()
                ):
                    id_doc_id_with_id_type_and_value = {x.id: x.id_type.name + "-" + x.value}
                    individual_id_docs.update(id_doc_id_with_id_type_and_value)

        # Check ID Docs of each group
        for ix in group:
            for x in ix.reg_ids:
                if x.id_type in self.supported_id_document_types and (
                    (not x.expiry_date) or x.expiry_date > date.today()
                ):
                    id_doc_id_with_id_type_and_value = {x.id: x.id_type.name + "-" + x.value}
                    individual_id_docs.update(id_doc_id_with_id_type_and_value)

        _logger.debug("Individual ID Documents: %s", individual_id_docs)
        rev_dict = {}
        for key, value in individual_id_docs.items():
            rev_dict.setdefault(value, set()).add(key)

        duplicate_ids = filter(lambda x: len(x) > 1, rev_dict.values())
        duplicate_ids = list(duplicate_ids)
        duplicate_ids = list(itertools.chain.from_iterable(duplicate_ids))
        _logger.debug("Reg_id IDS with Duplicated ID Documents: %s", duplicate_ids)

        duplicated_doc_ids = self.env["g2p.reg.id"].search([("id", "in", duplicate_ids)])
        individual_ids = [x.partner_id.id for x in duplicated_doc_ids]
        individual_ids = list(dict.fromkeys(individual_ids))

        group_with_duplicates = self.env["g2p.group.membership"].search(
            [("group", "in", group_ids), ("individual", "in", individual_ids)]
        )

        _logger.debug("group_with_duplicates: %s", group_with_duplicates)
        group_of_duplicates = {}
        for group_membership in group_with_duplicates:
            _logger.debug(
                f"group_membership.individual.id: {group_membership.individual.id} ->"
                f"{group_membership.group.id}"
            )
            if group_membership.individual.id not in group_of_duplicates:
                group_of_duplicates[group_membership.individual.id] = []
            group_of_duplicates[group_membership.individual.id].append(group_membership.group.id)

        _logger.debug("group_of_duplicates: %s", group_of_duplicates)
        for _individual, group_ids in group_of_duplicates.items():
            duplicate_beneficiaries = beneficiaries.filtered(lambda rec: rec.partner_id.id in group_ids)
            duplicate_beneficiariy_ids = duplicate_beneficiaries.mapped("id")

            self._record_duplicate(self, duplicate_beneficiariy_ids, "Duplicate ID Documents")

            duplicated_enrolled = duplicate_beneficiaries.filtered(lambda rec: rec.state == "enrolled")
            if len(duplicated_enrolled) == 1:
                # If there is only 1 enrolled that is duplicated,
                # the enrolled one should not be marked as duplicate.
                # otherwise if there is more than 1, then there is a problem!
                # TODO: check how to handle this
                duplicated_enrolled.write({"state": "enrolled"})
                duplicate_beneficiaries = duplicate_beneficiaries.filtered(
                    lambda rec: rec.state != "enrolled"
                )
            duplicate_beneficiaries.filtered(
                lambda rec: rec.state not in ["exited", "not_eligible", "duplicated"]
            ).write({"state": "duplicated"})

        return group_with_duplicates

    def _check_duplicate_by_individual(self, beneficiaries):
        """
        This method is used to check if there are any duplicates
        among the individuals id docs.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.debug("-" * 100)
        individual_ids = beneficiaries.mapped("partner_id.id")
        individuals = self.env["res.partner"].search([("id", "in", individual_ids)])
        _logger.debug("Checking ID Document Duplicates for: %s", individuals)

        individual_id_docs = {}
        # Check ID Documents of each individual
        for i in individuals:
            for x in i.reg_ids:
                if x.id_type in self.supported_id_document_types and (
                    (not x.expiry_date) or x.expiry_date > date.today()
                ):
                    id_doc_id_with_id_type_and_value = {x.id: x.id_type.name + "-" + x.value}
                    individual_id_docs.update(id_doc_id_with_id_type_and_value)

        _logger.debug("Individual ID Documents: %s", individual_id_docs)
        rev_dict = {}
        for key, value in individual_id_docs.items():
            rev_dict.setdefault(value, set()).add(key)

        duplicate_ids = filter(lambda x: len(x) > 1, rev_dict.values())
        duplicate_ids = list(duplicate_ids)
        duplicate_ids = list(itertools.chain.from_iterable(duplicate_ids))
        _logger.debug("Reg_id IDS with Duplicated ID Documents: %s", duplicate_ids)

        duplicated_doc_ids = self.env["g2p.reg.id"].search([("id", "in", duplicate_ids)])
        individual_ids = [x.partner_id.id for x in duplicated_doc_ids]
        individual_ids = list(dict.fromkeys(individual_ids))
        _logger.debug("Individual IDS with Duplicated ID Documents: %s", individual_ids)
        individual_program_membership = self.env["g2p.program_membership"].search(
            [
                ("partner_id", "in", individual_ids),
                ("program_id", "=", self.program_id.id),
            ]
        )

        for duplicates in individual_program_membership:
            duplicate_individuals = [duplicates.id]
            self._record_duplicate(self, duplicate_individuals, "Duplicate ID Documents")

            if duplicates.state == "enrolled":
                duplicates.write({"state": "duplicated"})

        return individual_program_membership


class PhoneNumberDeduplication(models.Model):
    """
    When this model is added, it should add also the
    PhoneNumberDeduplicationEligibilityManager to the eligibility
    criteria.
    """

    _name = "g2p.deduplication.manager.phone_number"
    _inherit = ["g2p.base.deduplication.manager", "g2p.manager.source.mixin"]
    _description = "Phone Number Deduplication Manager"

    # # if set, we verify that the phone number match a given regex
    # phone_regex = fields.Char(string="Phone Regex")

    def deduplicate_beneficiaries(self, states):
        for rec in self:
            duplicate_beneficiaries = []
            program = rec.program_id
            beneficiaries = program.get_beneficiaries(states)
            # duplicates
            _logger.debug("Deduplicate beneficiaries: %s", beneficiaries)
            if program.target_type == "group":
                duplicate_beneficiaries = self._check_duplicate_by_group_with_individual(beneficiaries)
            else:
                duplicate_beneficiaries = self._check_duplicate_by_individual(beneficiaries)
            return len(duplicate_beneficiaries)

    def _record_duplicate(self, manager, beneficiary_ids, reason):
        """
        This method is used to record a duplicate beneficiary.
        :param beneficiary: The beneficiary.
        :param reason: The reason.
        :param comment: The comment.
        :return:
        """

        # TODO: check this group does not exist already with the same manager and the same beneficiaries or
        #  a subset of them.
        #  1. If the state has been changed to no_duplicate,
        #  then we should not record it as duplicate unless there are
        #  additional beneficiaries in the group.
        #  2. Otherwise we update the record.

        _logger.debug("Record duplicate: %s", beneficiary_ids)

        existing_record = self.env["g2p.program.membership.duplicate"].search(
            [
                ("beneficiary_ids", "in", beneficiary_ids),
                ("state", "=", "duplicate"),
                ("deduplication_manager_id", "=", manager.id),
                ("reason", "=", reason),
            ]
        )
        if not existing_record:
            data = {
                "beneficiary_ids": [(6, 0, beneficiary_ids)],
                "state": "duplicate",
                "reason": reason,
                "deduplication_manager_id": manager,
            }
            _logger.debug("Record duplicate: %s", data)

            self.env["g2p.program.membership.duplicate"].create(data)

    def _check_duplicate_by_group_with_individual(self, beneficiaries):
        """
        This method is used to check if there are any duplicates among the individuals docs.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.debug("-" * 100)
        group_ids = beneficiaries.mapped("partner_id.id")
        group_memberships = self.env["g2p.group.membership"].search([("group", "in", group_ids)])
        group = self.env["res.partner"].search([("id", "in", group_ids)])
        _logger.debug("group_memberships: %s", group_memberships)

        individuals_ids = [rec.individual.id for rec in group_memberships]
        _logger.debug("individuals_ids: %s", individuals_ids)
        individual_phone_numbers = {}
        # Check Phone Numbers of each individual
        for i in group_memberships:
            for x in i.individual.phone_number_ids:
                phone_id_with_sanitized = {x.id: x.phone_sanitized}
                individual_phone_numbers.update(phone_id_with_sanitized)

        # Check Phone Numbers of each group
        for ix in group:
            for x in ix.phone_number_ids:
                phone_id_with_sanitized = {x.id: x.phone_sanitized}
                individual_phone_numbers.update(phone_id_with_sanitized)

        _logger.debug("Individual Phone Numbers: %s", individual_phone_numbers)

        rev_dict = {}
        for key, value in individual_phone_numbers.items():
            rev_dict.setdefault(value, set()).add(key)

        duplicate_ids = filter(lambda x: len(x) > 1, rev_dict.values())
        duplicate_ids = list(duplicate_ids)
        duplicate_ids = list(itertools.chain.from_iterable(duplicate_ids))
        _logger.debug("PhoneNumber IDS with Duplicated Phone Numbers: %s", duplicate_ids)

        duplicate_individuals_ids = self.env["g2p.phone.number"].search([("id", "in", duplicate_ids)])

        duplicate_individuals = [x.partner_id.id for x in duplicate_individuals_ids]
        duplicate_individuals = list(dict.fromkeys(duplicate_individuals))
        _logger.debug("Individual IDS with Duplicated Phone Numbers: %s", duplicate_individuals)

        group_with_duplicates = self.env["g2p.group.membership"].search(
            [("group", "in", group_ids), ("individual", "in", duplicate_individuals)]
        )

        _logger.debug("Group With Duplicates: %s", group_with_duplicates)

        group_of_duplicates = {}
        for group_membership in group_with_duplicates:
            _logger.debug(
                f"group_membership.individual.id: {group_membership.individual.id} ->"
                f"{group_membership.group.id}"
            )
            if group_membership.individual.id not in group_of_duplicates:
                group_of_duplicates[group_membership.individual.id] = []
            group_of_duplicates[group_membership.individual.id].append(group_membership.group.id)

        _logger.debug("group_of_duplicates: %s", group_of_duplicates)
        for _individual, group_ids in group_of_duplicates.items():
            duplicate_beneficiaries = beneficiaries.filtered(lambda rec: rec.partner_id.id in group_ids)
            duplicate_beneficiariy_ids = duplicate_beneficiaries.mapped("id")

            self._record_duplicate(self, duplicate_beneficiariy_ids, "Duplicate Phone Numbers")

            duplicated_enrolled = duplicate_beneficiaries.filtered(lambda rec: rec.state == "enrolled")
            if len(duplicated_enrolled) == 1:
                # If there is only 1 enrolled that is duplicated,
                # the enrolled one should not be marked as duplicate.
                # otherwise if there is more than 1, then there is a problem!
                # TODO: check how to handle this
                duplicated_enrolled.write({"state": "enrolled"})
                duplicate_beneficiaries = duplicate_beneficiaries.filtered(
                    lambda rec: rec.state != "enrolled"
                )
            duplicate_beneficiaries.filtered(
                lambda rec: rec.state not in ["exited", "not_eligible", "duplicated"]
            ).write({"state": "duplicated"})

        return group_with_duplicates

    def _check_duplicate_by_individual(self, beneficiaries):
        """
        This method is used to check if there are any duplicates among the individuals docs.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.debug("-" * 100)
        individual_ids = beneficiaries.mapped("partner_id.id")
        individuals = self.env["res.partner"].search([("id", "in", individual_ids)])
        _logger.debug("Checking Phone Duplicates for: %s", individuals)

        individual_phone_numbers = {}
        # Check Phone Numbers of each individual
        for i in individuals:
            for x in i.phone_number_ids:
                phone_id_with_sanitized = {x.id: x.phone_sanitized}
                individual_phone_numbers.update(phone_id_with_sanitized)

        _logger.debug("Individual Phone Numbers: %s", individual_phone_numbers)
        rev_dict = {}
        for key, value in individual_phone_numbers.items():
            rev_dict.setdefault(value, set()).add(key)

        duplicate_ids = filter(lambda x: len(x) > 1, rev_dict.values())
        duplicate_ids = list(duplicate_ids)
        duplicate_ids = list(itertools.chain.from_iterable(duplicate_ids))
        _logger.debug("PhoneNumber IDS with Duplicated Phone Numbers: %s", duplicate_ids)

        duplicated_phone_ids = self.env["g2p.phone.number"].search([("id", "in", duplicate_ids)])
        individual_ids = [x.partner_id.id for x in duplicated_phone_ids]
        individual_ids = list(dict.fromkeys(individual_ids))
        _logger.debug("Individual IDS with Duplicated Phone Numbers: %s", individual_ids)
        individual_program_membership = self.env["g2p.program_membership"].search(
            [
                ("partner_id", "in", individual_ids),
                ("program_id", "=", self.program_id.id),
            ]
        )

        for duplicates in individual_program_membership:
            duplicate_individuals = [duplicates.id]
            self._record_duplicate(self, duplicate_individuals, "Duplicate Phone Numbers")

            if duplicates.state == "enrolled":
                duplicates.write({"state": "duplicated"})

        return individual_program_membership


class IDPhoneEligibilityManager(models.Model):
    """
    Add the ID Document and Phone Number Deduplication in the Eligibility Manager
    """

    _inherit = "g2p.eligibility.manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_managers = [
            ("g2p.program_membership.manager.id_dedup", "ID Document Eligibility"),
            ("g2p.program_membership.manager.phone_number", "Phone Number Eligibility"),
        ]
        for new_manager in new_managers:
            if new_manager not in selection:
                selection.append(new_manager)
        return selection


class IDDocumentDeduplicationEligibilityManager(models.Model):
    """
    This model is used to check if a beneficiary has the required documents to be deduplicated.
    It uses the IDDocumentDeduplication configuration to perform the check
    """

    _name = "g2p.program_membership.manager.id_dedup"
    _inherit = ["g2p.program_membership.manager", "g2p.manager.source.mixin"]
    _description = "ID Document Deduplication Eligibility"

    eligibility_domain = fields.Text(string="Domain", default="[]")

    def _prepare_eligible_domain(self, membership):
        ids = membership.mapped("partner_id.id")
        registrant_ids = self.env["res.partner"].search([("id", "in", ids)])
        _logger.debug("Checking Registrants: %s", registrant_ids)
        registrant_ids_with_id = []
        for i in registrant_ids:
            if i.reg_ids:
                registrant_ids_with_id += [
                    i.id for x in i.reg_ids if (not x.expiry_date) or x.expiry_date > date.today()
                ]
        registrant_ids_with_id = list(dict.fromkeys(registrant_ids_with_id))
        _logger.debug("Eligible registrants with ID: %s", registrant_ids_with_id)
        domain = [("id", "in", registrant_ids_with_id)]
        domain += self._safe_eval(self.eligibility_domain)
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


class PhoneNumberDeduplicationEligibilityManager(models.Model):
    """
    This model is used to check if a beneficiary has a phone number to be deduplicated
    It uses the PhoneNumberDeduplication configuration to perform the check
    """

    _name = "g2p.program_membership.manager.phone_number"
    _inherit = ["g2p.program_membership.manager", "g2p.manager.source.mixin"]
    _description = "Phone Number Deduplication Eligibility"

    eligibility_domain = fields.Text(string="Domain", default="[]")

    def _prepare_eligible_domain(self, membership):
        ids = membership.mapped("partner_id.id")
        registrant_ids = self.env["res.partner"].search([("id", "in", ids)])
        _logger.debug("Checking Registrants: %s", registrant_ids)
        registrant_ids_with_phone = []
        for i in registrant_ids:
            if i.phone_number_ids:
                registrant_ids_with_phone += [i.id for x in i.phone_number_ids if not x.disabled]
        registrant_ids_with_phone = list(dict.fromkeys(registrant_ids_with_phone))
        _logger.debug("Eligible registrants with Phone: %s", registrant_ids_with_phone)

        domain = [("id", "in", registrant_ids_with_phone)]
        domain += self._safe_eval(self.eligibility_domain)
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
