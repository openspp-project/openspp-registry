from odoo import _, api, fields, models


class SppStarter(models.TransientModel):
    _name = "spp.starter"
    _description = "SPP Starter"

    STATE_SELECTION = [
        ("0", "Organization Setup"),
        ("1", "Registry Setup"),
        ("2", "Chosen Registry Setup"),
    ]
    SP_MIS_STATE_SELECTION = [
        ("0", "SP-MIS"),
        ("1", "Service Points"),
        ("2", "Cash Transfer"),
        ("3", "In-Kind Transfer"),
    ]
    FARMER_STATE_SELECTION = [
        ("0", "Farmer Registry"),
    ]

    state = fields.Selection(
        selection=STATE_SELECTION,
        required=True,
        default="0",
    )
    state_spmis = fields.Selection(
        selection=SP_MIS_STATE_SELECTION,
        required=True,
        default="0",
    )
    state_farmer = fields.Selection(
        selection=FARMER_STATE_SELECTION,
        required=True,
        default="0",
    )
    is_last_step = fields.Boolean(compute="_compute_is_last_step")
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
    registry_target = fields.Selection(
        selection=[
            ("spmis", "SP-MIS"),
            ("farmer", "Farmer Registry"),
        ],
        readonly=True,
        default="spmis",
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
    # STEP 3 SP-MIS
    sp_mis_demo_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To gauge whether demo module for SP-MIS is needed.",
    )

    # STEP 4 SP-MIS
    service_point_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To gauge whether additional logistics modules are needed.",
    )
    # STEP 5 SP-MIS
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
    # STEP 6 SP-MIS
    conducting_inkind_transfer = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To decide if modules for inventory management are needed.",
    )

    # STEP 3 Farmer Registry
    farmer_demo_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="no",
        help="To gauge whether demo module for farmer registry is needed.",
    )

    def _compute_is_last_step(self):
        for rec in self:
            if rec.registry_target == "spmis":
                rec.is_last_step = (
                    rec.state == rec.STATE_SELECTION[-1][0] and rec.state_spmis == rec.SP_MIS_STATE_SELECTION[-1][0]
                )
            if rec.registry_target == "farmer":
                rec.is_last_step = (
                    rec.state == rec.STATE_SELECTION[-1][0] and rec.state_farmer == rec.FARMER_STATE_SELECTION[-1][0]
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
        if state_int == len(self.STATE_SELECTION) - 1:
            if self.registry_target == "spmis" and int(self.state_spmis) > 0:
                self.state_spmis = str(int(self.state_spmis) - 1)
            elif self.registry_target == "farmer" and int(self.state_farmer) > 0:
                self.state_farmer = str(int(self.state_farmer) - 1)
            else:
                self.state = str(state_int - 1)
        else:
            self.state = str(max(state_int - 1, 0))
        return self._reopen()

    def action_next_state(self):
        self.ensure_one()
        state_int = int(self.state)
        if state_int < len(self.STATE_SELECTION) - 1:
            self.state = str(state_int + 1)
        if state_int == len(self.STATE_SELECTION) - 1:
            if self.registry_target == "spmis":
                self.state_spmis = str(int(self.state_spmis) + 1)
            if self.registry_target == "farmer":
                self.state_farmer = str(int(self.state_farmer) + 1)
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
        if self.registry_target == "spmis":
            res |= find_module("spp_base")
            res |= find_module("spp_programs")
            res |= find_module("spp_change_request")
            res |= find_module("spp_change_request_change_info")
            res |= find_module("spp_event_data")
            if self.sp_mis_demo_management == "yes":
                res |= find_module("spp_demo")
            if self.location_assignment == "yes":
                res |= find_module("spp_area")
            if self.service_point_management == "yes":
                res |= find_module("spp_service_points")
            if self.cash_transfer_needed == "yes":
                res |= find_module("spp_entitlement_cash")
            if self.bank_details_needed == "yes":
                res |= find_module("g2p_bank")
            if self.conducting_inkind_transfer == "yes":
                res |= find_module("spp_entitlement_in_kind")

        if self.registry_target == "farmer":
            # TODO: needs to change this once the module for farmer registry default UI is created
            res |= find_module("spp_farmer_registry_base")
            if self.location_assignment == "yes":
                res |= find_module("spp_area_gis")
            if self.farmer_demo_management == "yes":
                res |= find_module("spp_farmer_registry_demo")
                res |= find_module("spp_programs")

        if self.id_management == "yes":
            res |= find_module("spp_idpass")

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
