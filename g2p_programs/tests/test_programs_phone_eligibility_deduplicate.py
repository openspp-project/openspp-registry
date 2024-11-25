import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class ProgramTestPhoneEligibilityDeduplicate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Initial Setup of Variables
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "family_name": "Doe",
                "given_name": "John",
                "name": "John Doe",
                "is_group": False,
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "family_name": "Doe",
                "given_name": "Jane",
                "name": "Jane Doe",
                "is_group": False,
            }
        )
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
            }
        )
        cls.group_2 = cls.env["res.partner"].create(
            {
                "name": "Group 2",
                "is_group": True,
            }
        )

        currency_id = cls.env.user.company_id.currency_id and cls.env.user.company_id.currency_id.id or None

        cls.program_1_id = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 1",
                "currency_id": currency_id,
                "amount_per_cycle": 20,
                "amount_per_individual_in_group": 10,
            }
        )

        # Add Program
        program_1_form = cls.program_1_id.create_program()
        program_1_id = program_1_form["res_id"]
        cls.program_1 = cls.env["g2p.program"].search([("id", "=", program_1_id)])
        cls.program_2_id = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 2",
                "currency_id": currency_id,
                "amount_per_cycle": 100,
                "amount_per_individual_in_group": 10,
            }
        )
        program_2_form = cls.program_2_id.create_program()
        program_2_id = program_2_form["res_id"]
        cls.program_2 = cls.env["g2p.program"].search([("id", "=", program_2_id)])
        cls.program_1.write({"target_type": "individual"})
        cls.program_2.write({"target_type": "group"})

        # Add Beneficiaries
        cls.program_1.write({"program_membership_ids": [(0, 0, {"partner_id": cls.registrant_1.id})]})
        cls.program_1.write({"program_membership_ids": [(0, 0, {"partner_id": cls.registrant_2.id})]})
        cls.program_2.write({"program_membership_ids": [(0, 0, {"partner_id": cls.group_1.id})]})
        cls.program_2.write({"program_membership_ids": [(0, 0, {"partner_id": cls.group_2.id})]})
        # Add Phone Eligibility Manager
        cls.manager_1 = cls.env["g2p.program_membership.manager.phone_number"].create(
            {
                "name": "Phone Manager 1",
                "program_id": cls.program_1.id,
            }
        )
        cls.program_1.write(
            {
                "eligibility_managers": [
                    (
                        0,
                        0,
                        {
                            "manager_ref_id": "g2p.program_membership.manager.phone_number, %s"
                            % cls.manager_1.id,
                            "manager_id": cls.manager_1.id,
                        },
                    )
                ]
            }
        )
        cls.manager_2 = cls.env["g2p.program_membership.manager.phone_number"].create(
            {
                "name": "Phone Manager 2",
                "program_id": cls.program_2.id,
            }
        )
        cls.program_2.write(
            {
                "eligibility_managers": [
                    (
                        0,
                        0,
                        {
                            "manager_ref_id": "g2p.program_membership.manager.phone_number, %s"
                            % cls.manager_2.id,
                            "manager_id": cls.manager_2.id,
                        },
                    )
                ]
            }
        )
        # Enroll Beneficiaries without Phones expecting NONE will be enrolled
        cls.program_1.enroll_eligible_registrants()
        cls.program_2.enroll_eligible_registrants()
        # Beneficiaries Add IDS

        cls.registrant_1.write(
            {
                "phone_number_ids": [
                    (
                        0,
                        0,
                        {
                            "phone_no": "9123456789",
                        },
                    )
                ]
            }
        )
        cls.registrant_2.write(
            {
                "phone_number_ids": [
                    (
                        0,
                        0,
                        {
                            "phone_no": "9123456789",
                        },
                    )
                ]
            }
        )
        cls.group_1.write(
            {
                "phone_number_ids": [
                    (
                        0,
                        0,
                        {
                            "phone_no": "9123456789",
                        },
                    )
                ]
            }
        )
        cls.group_2.write(
            {
                "phone_number_ids": [
                    (
                        0,
                        0,
                        {
                            "phone_no": "9123456789",
                        },
                    )
                ]
            }
        )

        # Try Enrolling now when Phones has been ADDED
        cls.program_1.enroll_eligible_registrants()
        cls.program_2.enroll_eligible_registrants()

    def test_01_deduplication(self):
        # Test the Deduplication on the Programs now with ID Deduplication Managers

        # Add first the Phone Deduplication
        self.manager_1 = self.env["g2p.deduplication.manager.phone_number"].create(
            {
                "name": "Phone Manager 1",
                "program_id": self.program_1.id,
            }
        )
        if self.manager_1:
            self.program_1.write(
                {
                    "deduplication_managers": [
                        (
                            0,
                            0,
                            {
                                "manager_ref_id": "g2p.deduplication.manager.phone_number, %s"
                                % self.manager_1.id,
                                "manager_id": self.manager_1.id,
                            },
                        )
                    ]
                }
            )
            if len(self.program_1.deduplication_managers) > 0:
                self.program_1.deduplicate_beneficiaries()
                # TODO: check this assert line
                # self.assertEqual(
                #     self.program_1.duplicate_membership_count,
                #     2,
                #     "Program Testing: Expected Duplicate count exceeded",
                # )
        # Add first the Phone Deduplication Manager

        self.manager_2 = self.env["g2p.deduplication.manager.phone_number"].create(
            {
                "name": "Phone Manager 2",
                "program_id": self.program_2.id,
            }
        )
        if self.manager_2:
            self.program_2.write(
                {
                    "deduplication_managers": [
                        (
                            0,
                            0,
                            {
                                "program_id": self.program_2.id,
                                "manager_ref_id": "g2p.deduplication.manager.phone_number, %s"
                                % self.manager_2.id,
                                "manager_id": self.manager_2.id,
                            },
                        )
                    ]
                }
            )
            # Add Members to the Group with Duplicate IDs
            self.group_1.write({"group_membership_ids": [(0, 0, {"individual": self.registrant_1.id})]})
            self.group_2.write({"group_membership_ids": [(0, 0, {"individual": self.registrant_2.id})]})
            if len(self.program_2.deduplication_managers) > 0:
                self.program_2.deduplicate_beneficiaries()
                self.assertEqual(
                    self.program_2.duplicate_membership_count,
                    0,
                    "Program Testing: Expected Duplicate count exceeded",
                )
