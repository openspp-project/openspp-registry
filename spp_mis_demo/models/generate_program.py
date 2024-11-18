# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import hashlib
import logging
import random

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OpenSPPGenerateProgramData(models.Model):
    _name = "spp.generate.program.data"
    _description = "Generate Program Data"

    name = fields.Char()
    num_programs = fields.Integer("Number of Programs", default=1)
    num_beneficicaries = fields.Integer("Number of Beneficiary", default=1)
    num_cycles = fields.Integer("Number of Cycles", default=1)
    # beneficiary_ids = fields.Many2many(
    #     "g2p.program_membership", string="Beneficiaries", readonly=False
    # )
    cycle_ids = fields.Many2many("g2p.cycle", string="Cycle", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated Program"),
            ("approve", "Approved All Entitlements"),
        ],
        default="draft",
    )

    def generate_program_data(self):
        """
        Generate program data for testing
        Returns:

        """

        group_target_type_range = ["group", "individual"]
        cycle_auto_approve_range = [True, False]
        cycle_duration_range = [30] * 5 + [15, 60]

        for i in range(0, self.num_programs):
            program_name = f"GenProgram {i+1}"
            target_type = random.choice(group_target_type_range)

            program_id = "demo." + hashlib.md5(f"{program_name} {i}".encode()).hexdigest()

            program_data = {
                "id": program_id,
                "name": program_name,
                "target_type": target_type,
            }

            # # create_program_id = program_data
            create_program_id = self.env["g2p.program"].create(program_data)
            _logger.debug(f"program--- {create_program_id}: {create_program_id.target_type}")

            #  Default Enrollment indicator

            domain = [("is_registrant", "=", True)]
            eligibility_domain = ["&", ["is_registrant", "=", True]]
            if target_type == "group":
                domain.extend([("is_group", "=", True)])
                eligibility_domain.append(["is_group", "=", True])
            else:
                domain.extend([("is_group", "=", False)])
                eligibility_domain.append(["is_group", "!=", True])

            vals = {}
            #  Default Eligibility Manager
            def_eli_mgr_obj = "g2p.program_membership.manager.default"
            eligibility_manager_data = {
                "name": "Default",
                "program_id": create_program_id.id,
                "eligibility_domain": str(eligibility_domain),
            }

            def_eli_mgr_id = self.env[def_eli_mgr_obj].create(eligibility_manager_data)

            # Add a new record to eligibility manager parent model
            eli_man_obj = self.env["g2p.eligibility.manager"]
            eli_mgr_id = eli_man_obj.create(
                {
                    "program_id": create_program_id.id,
                    "manager_ref_id": f"{def_eli_mgr_obj},{str(def_eli_mgr_id.id)}",
                }
            )

            vals.update({"eligibility_managers": [(4, eli_mgr_id.id)]})

            auto_approve_entitlements = random.choice(cycle_auto_approve_range)
            cycle_duration = random.choice(cycle_duration_range)
            # Cycle Manageer
            # TODO: approver_group_id
            def_cycle_mgr_obj = "g2p.cycle.manager.default"
            cycle_manager_data = {
                "name": "Default",
                "program_id": create_program_id.id,
                "auto_approve_entitlements": auto_approve_entitlements,
                "cycle_duration": cycle_duration,
                "approver_group_id": self.env.ref("g2p_registry_base.group_g2p_admin").id,
            }
            def_cycle_mgr_id = self.env[def_cycle_mgr_obj].create(cycle_manager_data)

            # Add a new record to cycle manager parent model
            cycle_man_obj = self.env["g2p.cycle.manager"]
            cycle_man_id = cycle_man_obj.create(
                {
                    "program_id": create_program_id.id,
                    "manager_ref_id": f"{def_cycle_mgr_obj},{str(def_cycle_mgr_id.id)}",
                }
            )
            vals.update({"cycle_managers": [(4, cycle_man_id.id)]})

            # # Entitle Manageer
            # # TODO: entitlement_validation_group_id
            def_prog_ent_mgr_obj = "g2p.program.entitlement.manager.default"
            entitlement_manager_data = {
                "name": "Default",
                "program_id": create_program_id.id,
                "amount_per_cycle": random.choice([1000, 2000, 3000]),
                "amount_per_individual_in_group": random.choice([1000, 2000, 3000]),
                "max_individual_in_group": random.randint(0, 10),
                "entitlement_validation_group_id": None,
            }

            def_prog_ent_mgr_id = self.env[def_prog_ent_mgr_obj].create(entitlement_manager_data)

            # Add a new record to entitlement manager parent model
            prog_ent_obj = self.env["g2p.program.entitlement.manager"]
            prog_ent_id = prog_ent_obj.create(
                {
                    "program_id": create_program_id.id,
                    "manager_ref_id": f"{def_prog_ent_mgr_obj},{str(def_prog_ent_mgr_id.id)}",
                }
            )
            vals.update({"entitlement_managers": [(4, prog_ent_id.id)]})

            # Create Beneficiaries
            benificiaries_count = self.num_beneficicaries
            registrant_ids = self.env["res.partner"].search(domain, limit=benificiaries_count).ids

            _logger.debug(f"registrant_ids-- {len(registrant_ids)} : {registrant_ids}")

            benificiary_lines = []
            for r_id in range(len(registrant_ids)):
                benificiary_data = {
                    "partner_id": registrant_ids[r_id],
                    "program_id": create_program_id.id,
                }
                benificiary_lines.append((0, 0, benificiary_data))

            vals.update({"program_membership_ids": benificiary_lines})

            # self.cycle_ids = [(4, beneficiary_id.id for beneficiary_id in benificiary_lines)]
            # Complete the program data
            create_program_id.update(vals)

            # Enroll Registrant
            create_program_id.enroll_eligible_registrants()

            # Create New Cycle
            # TODO: generate cycles
            program_manager = create_program_id.get_manager(create_program_id.MANAGER_PROGRAM)

            ######################################################################################
            # cycle_id = program_manager.new_cycle()
            for _i in range(0, self.num_cycles):
                cycle_id = program_manager.new_cycle()

                _logger.debug(f"cycle--- {cycle_id}")

                # Create Entitlements
                cycle_manager = create_program_id.get_manager(create_program_id.MANAGER_CYCLE)
                cycle_manager.prepare_entitlements(cycle_id)

                self.cycle_ids = [(4, cycle_id.id)]

                # # Create Program Funds
                entitlement_ids = cycle_id.entitlement_ids

                # # initital_amount
                total_initial_amount = sum(a.initial_amount for a in entitlement_ids)

                program_fund_data = {
                    "name": "Draft",
                    "program_id": create_program_id.id,
                    "amount": total_initial_amount,
                }

                # # Create and Post Program fund
                create_prog_fund_id = self.env["g2p.program.fund"].create(program_fund_data)
                create_prog_fund_id.post_fund()

                if create_prog_fund_id.state == "posted":
                    cycle_id.to_approve()
                    _logger.debug(f"cycle_id--- {cycle_id.state}")

                # # Create Helpdesk Tickets in Cycle
                # Todo: Create Helpdesk Tickets in Cycle when the new helpdesk module has been created.
                # cycle_beneficiary_ids = cycle_id.get_beneficiaries(["enrolled"]).mapped("partner_id.id")
                # for beneficiary_id in cycle_beneficiary_ids:
                #     tx_name = random.choice(ticket_name_range)
                #     tx_desc = random.choice(ticket_disc_cycle_range)
                #     self.env["helpdesk.ticket"].create(
                #         {
                #             "name": tx_name,
                #             "partner_id": beneficiary_id,
                #             "cycle_id": cycle_id.id,
                #             "description": f"{tx_name} in {tx_desc}",
                #             "priority": str(random.randint(0, 3)),
                #         }
                #     )

            ######################################################################################
            # Create Helpdesk Tickets in Beneficiaries
            # Todo: Create Helpdesk Tickets in Cycle when the new helpdesk module has been created.
            # beneficiary_ids = create_program_id.get_beneficiaries(["enrolled"]).mapped("partner_id.id")
            #
            # for beneficiary_id in beneficiary_ids:
            #     tx_name = random.choice(ticket_name_range)
            #     tx_desc = random.choice(ticket_disc_beneficiary_range)
            #     self.env["helpdesk.ticket"].create(
            #         {
            #             "name": tx_name,
            #             "partner_id": beneficiary_id,
            #             "program_id": create_program_id.id,
            #             "description": f"{tx_name} in {tx_desc}",
            #             "priority": str(random.randint(0, 3)),
            #         }
            #     )

            if self.state == "draft":
                self.update({"state": "generate"})

            # _logger.info("-" * 80)
            # _logger.info(
            #     json.dumps(
            #         {
            #             "program_data": program_data,
            #             "eligibility_manager_data": eligibility_manager_data,
            #             "cycle_manager_data": cycle_manager_data,
            #             "entitlement_manager_data": entitlement_manager_data,
            #         },
            #         indent=4,
            #     )
            # )

    def approve_entitlements(self):
        if self.cycle_ids:
            for cycle in self.cycle_ids:
                if cycle.state == "to_approve":
                    for entitlement in cycle.entitlement_ids:
                        if entitlement.state == "draft":
                            entitlement.approve_entitlement()
                        # cycle.approve()
        self.update({"state": "approve"})
