from odoo import _, api, fields, models


class SppStarter(models.TransientModel):
    _name = "spp.starter"
    _description = "SPP Starter"

    state = fields.Selection(
        selection=[
            ("0", "Organization"),
            ("1", "Registry"),
            ("2", "Service Points"),
            ("3", "Cash Transfer"),
            ("4", "In-Kind Transfer"),
            ("5", "Grievance Redress Mechanism"),
        ],
        required=True,
        default="0",
    )
    # STEP 1
    org_name = fields.Char(
        readonly=True,
        help="Identify the company for record-keeping and customization.",
    )
    org_address = fields.Char(
        readonly=True,
        help="For record-keeping and location-based features.",
    )
    org_phone = fields.Char(
        readonly=True,
        help="For contact and possibly for integrations like SMS alerts.",
    )
    org_currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
        context={"active_test": False},
        help="To set the default currency for financial transactions.",
    )
    # STEP 2
    managing_target = fields.Selection(
        selection=[
            ("individual", "Individual"),
            ("group", "Group"),
            ("both", "Both"),
        ],
        readonly=True,
        default="both",
        help="To customize data models and interfaces.",
    )
    location_assignment = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To decide whether geo-tagging modules are needed.",
    )
    id_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To determine if identity management modules should be installed.",
    )
    # STEP 3
    service_point_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To gauge whether additional logistics modules are needed.",
    )
    # STEP 4
    cash_transfer_needed = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To install cash transfer modules.",
    )
    bank_details_needed = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To add functionality for storing financial information.",
    )
    # STEP 5
    conducting_inkind_transfer = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To decide if modules for inventory management are needed.",
    )
    # STEP 6
    complaint_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To add modules for complaint management if needed.",
    )

    def action_done(self):
        self.ensure_one()
        self._adjust_main_company_details()
        modules = self._install_modules()
        modules.button_immediate_install()
        self._remove_default_products_if_needed()
        self._remove_fake_apps_menu()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_last_state(self):
        self.ensure_one()
        state_int = int(self.state)
        if state_int > 0:
            self.state = str(state_int - 1)
        return self._reopen()

    def action_next_state(self):
        self.ensure_one()
        state_int = int(self.state)
        if state_int < 5:
            self.state = str(state_int + 1)
        return self._reopen()

    def _adjust_main_company_details(self):
        self.ensure_one()
        self.env.company.sudo().write(
            {
                "name": self.org_name,
                "street": self.org_address,
                "phone": self.org_phone,
                "currency_id": self.org_currency_id.id,
            }
        )

    def _install_modules(self):
        self.ensure_one()

        def find_module(module_name):
            return self.env.ref(f"base.module_{module_name}", raise_if_not_found=False)

        res = find_module("theme_openspp_muk")
        if self.managing_target == "individual":
            res |= find_module("g2p_registry_individual")
        if self.managing_target == "group":
            res |= find_module("g2p_registry_group")
        if self.managing_target == "both":
            res |= find_module("g2p_registry_membership")
        if self.location_assignment == "yes":
            res |= find_module("spp_area")
        if self.id_management == "yes":
            res |= find_module("spp_idpass")
        if self.service_point_management == "yes":
            res |= find_module("spp_service_points")
        if self.cash_transfer_needed == "yes":
            res |= find_module("spp_entitlement_cash")
        if self.bank_details_needed == "yes":
            res |= find_module("g2p_bank")
        if self.conducting_inkind_transfer == "yes":
            res |= find_module("spp_entitlement_in_kind")
        return res

    def _remove_default_products_if_needed(self):
        self.ensure_one()
        if self.conducting_inkind_transfer != "yes" or "product.template" not in self.env:
            return
        all_products = self.env["product.template"].sudo().search([])
        return all_products.write({"active": False})

    @api.model
    def _remove_fake_apps_menu(self):
        return self.env["ir.config_parameter"].sudo().set_param("spp_starter.show_spp_starter", "False")

    def _reopen(self):
        self.ensure_one()
        return {
            "name": _(self._description),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
