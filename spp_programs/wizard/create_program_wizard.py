# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.osv.expression import AND, OR
from odoo.tools import safe_eval

# from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    @api.model
    def _get_admin_area_domain(self):
        return [("kind", "=", self.env.ref("spp_area_base.admin_area_kind").id)]

    admin_area_ids = fields.Many2many("spp.area", domain=_get_admin_area_domain)

    is_one_time_distribution = fields.Boolean("One-time Distribution")

    # SQL-base Eligibility Manager
    eligibility_kind = fields.Selection(
        [("default_eligibility", "Default")],
        "Eligibility Manager",
        default="default_eligibility",
    )

    id_type = fields.Many2one("g2p.id.type", "ID Type to store in entitlements")
    view_id = fields.Many2one(
        "ir.ui.view",
        "Program UI Template",
        domain="[('model', '=', 'g2p.program'), " "('type', '=', 'form')," "('inherit_id', '=', False),]",
        default=lambda self: self._get_default_program_ui(),
    )

    def _get_default_program_ui(self):
        return self.env.ref("g2p_programs.view_program_list_form")

    @api.onchange("admin_area_ids")
    def on_admin_area_ids_change(self):
        eligibility_domain = self.eligibility_domain
        domain = []
        if eligibility_domain not in [None, "[]"]:
            # Do not remove other filters
            # Convert the string to list of tuples
            domain = safe_eval.safe_eval(eligibility_domain)
            # get the area_center_id from the list
            area_dom = [flt for flt in domain if "area_id" in flt]
            if area_dom:
                domain.remove(area_dom[0])

        if self.admin_area_ids:
            area_ids = self.admin_area_ids.ids
            domain.append(("area_id", "in", tuple(area_ids)))
        eligibility_domain = str(self._insert_domain_operator(domain))

        self.eligibility_domain = eligibility_domain

    def _insert_domain_operator(self, domain):
        """Insert operator to the domain"""
        if not domain:
            return domain
        operator_used = AND
        if domain[0] == "|":
            operator_used = OR
        new_domain = []
        domain = list(filter(lambda a: a not in ["&", "|", "!"], domain))
        for dom in domain:
            new_domain = operator_used([new_domain, [dom]])
        return new_domain

    def create_program(self):
        self._check_required_fields()
        for rec in self:
            program_vals = rec.get_program_vals()
            program = self.env["g2p.program"].create(program_vals)

            program_id = program.id
            vals = {}

            # Set Default Eligibility Manager settings
            vals.update(rec._get_eligibility_manager(program_id))

            # Set Default Cycle Manager settings
            # Add a new record to default cycle manager model

            cycle_manager_default_val = rec.get_cycle_manager_default_val(program_id)
            def_mgr = self.env["g2p.cycle.manager.default"].create(cycle_manager_default_val)

            # Add a new record to cycle manager parent model

            cycle_manager_val = rec.get_cycle_manager_val(program_id, def_mgr)
            mgr = self.env["g2p.cycle.manager"].create(cycle_manager_val)

            vals.update({"cycle_managers": [(4, mgr.id)]})

            # Set Default Entitlement Manager
            vals.update(rec._get_entitlement_manager(program_id))

            vals.update({"is_one_time_distribution": rec.is_one_time_distribution})

            # Complete the program data
            program.update(vals)

            if rec.import_beneficiaries == "yes":
                rec.program_wizard_import_beneficiaries(program)

            if rec.is_one_time_distribution:
                program.create_new_cycle()

            view_id = self.env.ref("g2p_programs.view_program_list_form")
            if rec.view_id:
                view_id = rec.view_id

            program.view_id = view_id.id

            # Open the newly created program
            return {
                "name": _("Programs"),
                "view_mode": "form",
                "res_model": "g2p.program",
                "res_id": program_id,
                "view_id": view_id.id,
                "type": "ir.actions.act_window",
                "target": "current",
            }

    def _get_default_eligibility_manager_val(self, program_id):
        return {
            "name": "Default",
            "program_id": program_id,
            "admin_area_ids": self.admin_area_ids,
            "eligibility_domain": self.eligibility_domain,
        }

    def _get_eligibility_managers_val(self, program_id, def_mgr):
        return {
            "program_id": program_id,
            "manager_ref_id": f"{def_mgr._name},{str(def_mgr.id)}",
        }

    def _get_eligibility_manager(self, program_id):
        val = {}
        if self.eligibility_kind == "default_eligibility":
            # Add a new record to default eligibility manager model
            default_eligibility_manager_val = self._get_default_eligibility_manager_val(program_id)
            def_mgr = self.env["g2p.program_membership.manager.default"].create(default_eligibility_manager_val)

            # Add a new record to eligibility manager parent model
            eligibility_manager_val = self._get_eligibility_managers_val(program_id, def_mgr)
            mgr = self.env["g2p.eligibility.manager"].create(eligibility_manager_val)

            val = {"eligibility_managers": [(4, mgr.id)]}
        return val

    def program_wizard_import_beneficiaries(self, program):
        eligibility_managers = program.get_managers(program.MANAGER_ELIGIBILITY)
        eligibility_managers[0].import_eligible_registrants(state="enrolled")

    def get_cycle_manager_val(self, program_id, cycle_manager_default):
        return {
            "program_id": program_id,
            "manager_ref_id": f"{cycle_manager_default._name},{str(cycle_manager_default.id)}",
        }

    def get_cycle_manager_default_val(self, program_id):
        return {
            "name": "Default",
            "program_id": program_id,
            "auto_approve_entitlements": self.auto_approve_entitlements,
            "cycle_duration": self.cycle_duration,
            "approver_group_id": self.approver_group_id.id or None,
            **self._get_recurrent_field_values(),
        }

    def get_program_vals(self):
        # Create a new journal for this program
        journal_id = self.create_journal(self.name, self.currency_id.id)

        return {
            "name": self.name,
            "journal_id": journal_id,
            "target_type": self.target_type,
        }

    def _reopen_self(self):
        return {
            "name": "Set Program Settings",
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _get_entitlement_manager(self, program_id):
        val = None
        if self.entitlement_kind == "default":
            # Add a new record to default entitlement manager model
            def_mgr_obj = "g2p.program.entitlement.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "amount_per_cycle": self.amount_per_cycle,
                    "amount_per_individual_in_group": self.amount_per_individual_in_group,
                    "transfer_fee_pct": self.transfer_fee_pct,
                    "transfer_fee_amt": self.transfer_fee_amt,
                    "max_individual_in_group": self.max_individual_in_group,
                    "entitlement_validation_group_id": self.entitlement_validation_group_id.id,
                    "id_type": self.id_type.id,
                }
            )
            # Add a new record to entitlement manager parent model
            man_obj = self.env["g2p.program.entitlement.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": f"{def_mgr_obj},{str(def_mgr.id)}",
                }
            )
            val = {"entitlement_managers": [(4, mgr.id)]}
        return val
