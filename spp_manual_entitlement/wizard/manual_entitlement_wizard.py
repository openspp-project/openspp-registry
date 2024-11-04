# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import base64
import csv
import io
import logging
from io import BytesIO

from xlrd import open_workbook

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.g2p_programs.models import constants

_logger = logging.getLogger(__name__)


class SPPPrepareManualEntitlementWizard(models.TransientModel):
    _name = "spp.manual.entitlement.wizard"
    _description = "Manual Entitlement Wizard"

    cycle_membership_ids = fields.One2many("spp.cycle.membership.transient", "manual_entitlement_id")
    upload_cycle_membership_ids = fields.One2many("spp.upload.cycle.membership", "manual_entitlement_id")
    cycle_id = fields.Many2one("g2p.cycle", "Cycle")
    step = fields.Selection(
        [
            ("step1", "Step 1"),
            ("step2a", "Step 2"),
            ("step2b_1", "Step 2"),
            ("step2b_2", "Step 2"),
            ("step3", "Step 3"),
        ],
        default="step1",
    )
    file = fields.Binary()
    final_file = fields.Binary()
    filename = fields.Char()

    @api.onchange("file")
    def file_change(self):
        if self.file:
            file = self.filename.split(".")
            file_ext = file[len(file) - 1]
            if file_ext not in ("xlsx", "csv"):
                raise UserError(_("Only Excel and CSV files are allowed!"))

    def start_import(self):
        for rec in self:
            import_vals = []

            file = rec.filename.split(".")
            file_ext = file[len(file) - 1]

            if file_ext == "csv":
                csv_data = base64.b64decode(rec.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=",")
                file_reader.extend(csv_reader)
                curr_row = 0
                for row in file_reader:
                    if curr_row != 0:
                        vals = {"partner_id": row[0], "entitlement_amount": row[1]}
                        import_vals.append(Command.create(vals))

                    curr_row += 1

            else:
                try:
                    inputx = BytesIO()
                    inputx.write(base64.decodebytes(rec.file))
                except TypeError as e:
                    raise ValidationError(_("ERROR: {}").format(e)) from e

                book = open_workbook(file_contents=inputx.getvalue())
                sheet = book.sheet_by_index(0)
                for row in range(1, sheet.nrows):
                    vals = {
                        "partner_id": sheet.cell(row, 0).value,
                        "entitlement_amount": sheet.cell(row, 1).value,
                    }
                    import_vals.append(Command.create(vals))

            rec.update({"upload_cycle_membership_ids": import_vals})
            self.step = "step2b_2"
            title = "Data Imported"
            return self._reopen_self(title)

    def search_existing_entitlement(self, registrant):
        current_entitlement = self.env["g2p.entitlement"].search(
            [("partner_id", "=", registrant), ("cycle_id", "=", self.cycle_id.id)]
        )
        if current_entitlement:
            return True
        return False

    def finalize_import(self):
        for rec in self:
            beneficiary_vals = [(Command.clear())]
            beneficiary_count = 0
            for beneficiary in rec.upload_cycle_membership_ids:
                registrant = self.env["res.partner"].search([("spp_id", "=", beneficiary.partner_id)])
                if registrant:
                    with_existing_entitlement = self.search_existing_entitlement(registrant.id)
                    if not with_existing_entitlement:
                        partner = self.env["g2p.cycle.membership"].search(
                            [("partner_id", "=", registrant.id), ("cycle_id", "=", rec.cycle_id.id)]
                        )
                        if partner:
                            beneficiary_count += 1
                            vals = {
                                "partner_id": partner.partner_id.id,
                                "entitlement_amount": beneficiary.entitlement_amount,
                            }
                            beneficiary_vals.append(Command.create(vals))

            if beneficiary_count > 0:
                rec.update({"cycle_membership_ids": beneficiary_vals})
                self.step = "step3"
                title = "Finalize entitlement amount"
                return self._reopen_self(title)
            else:
                raise UserError(
                    _(
                        "Nothing to Import, either the registrant doesn't exists "
                        "or there's an existing entitlement for the registrant in this cycle. "
                        "Please check your excel or csv file."
                    )
                )

    def step_manual_select(self):
        if not self.cycle_membership_ids:
            raise UserError(_("All beneficiaries for this cycle has entitlement. Can't proceed!"))
        self.step = "step2a"
        title = "Beneficiary Selection"
        return self._reopen_self(title)

    def step_upload_csv(self):
        if not self.cycle_membership_ids:
            raise UserError(_("All beneficiaries for this cycle has entitlement. Can't proceed!"))
        self.step = "step2b_1"
        title = "CSV Upload"
        return self._reopen_self(title)

    def step_input_entitlement_amounts(self):
        selected = self.cycle_membership_ids.filtered(lambda f: f.selected).mapped("id")

        if not selected:
            raise UserError(_("No beneficiary selected!"))

        not_selected = self.cycle_membership_ids.filtered(lambda f: not f.selected).mapped("id")

        if not_selected:
            to_remove = []

            for beneficiary in not_selected:
                to_remove.append(Command.unlink(beneficiary))

            self.update({"cycle_membership_ids": to_remove})

        self.step = "step3"
        title = "Enter entitlement amount"
        return self._reopen_self(title)

    def create_entitlement(self):
        for rec in self:
            cycle_manager = rec.cycle_id.program_id.get_manager(constants.MANAGER_CYCLE)
            if not cycle_manager:
                raise UserError(_("No Cycle Manager defined."))

            return cycle_manager.prepare_manual_entitlements(rec.cycle_id, rec.cycle_membership_ids)

    def _reopen_self(self, title):
        return {
            "name": _("Manual Entitlement: %s", title),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }


class SPPCycleMembership(models.TransientModel):
    _name = "spp.cycle.membership.transient"
    _description = "Cycle Membership Transient"

    selected = fields.Boolean(default=False)
    partner_id = fields.Many2one("res.partner", "Registrant", help="A beneficiary", required=True, index=True)
    entitlement_amount = fields.Float()
    manual_entitlement_id = fields.Many2one("spp.manual.entitlement.wizard")


class SPPUploadedCycleMembership(models.TransientModel):
    _name = "spp.upload.cycle.membership"
    _description = "Upload Cycle Membership"

    partner_id = fields.Char("Registrant")
    entitlement_amount = fields.Float()
    manual_entitlement_id = fields.Many2one("spp.manual.entitlement.wizard")
