import base64
import os

from odoo import _
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestManualEntitlement(TransactionCase):
    @staticmethod
    def get_file_path_1():
        return f"{os.path.dirname(os.path.abspath(__file__))}/test_entitlement.xlsx"

    @staticmethod
    def get_file_path_2():
        return f"{os.path.dirname(os.path.abspath(__file__))}/test_entitlement.csv"

    @staticmethod
    def get_file_path_3():
        return f"{os.path.dirname(os.path.abspath(__file__))}/test_entitlement.pdf"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "name": "Registrant 1 [MANUAL ENTITLEMENT TEST]",
                "is_registrant": True,
                "is_group": True,
                "spp_id": "GRP_VKW59J49",
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "name": "Registrant 2 [MANUAL ENTITLEMENT TEST]",
                "is_registrant": True,
                "is_group": True,
                "spp_id": "GRP_VKW59J48",
            }
        )
        cls.program_wizard = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [MANUAL ENTITLEMENT TEST]",
                "entitlement_kind": "manual_cash",
            }
        )
        cls.program_wizard.create_program()
        cls.program = cls.env["g2p.program"].search([("name", "=", "Program 1 [MANUAL ENTITLEMENT TEST]")])

        membership_vals = [
            {
                "partner_id": cls.registrant_1.id,
                "program_id": cls.program.id,
            },
            {
                "partner_id": cls.registrant_2.id,
                "program_id": cls.program.id,
            },
        ]

        cls.env["g2p.program_membership"].create(membership_vals)
        cls.program.verify_eligibility()
        cls.program.enroll_eligible_registrants()
        cls.program.create_new_cycle()

    def set_cycle(self):
        cycle = self.program.cycle_ids[0]
        cycle.copy_beneficiaries_from_program()
        return cycle

    def test_01_check_manual_entitlement(self):
        cycle = self.set_cycle()

        cycle._compute_is_manual_entitlement()
        self.assertEqual(cycle.is_manual_entitlement, True, "Correct value")
        self.assertFalse(cycle.search_existing_entitlement(self.registrant_1.id), "Correct value")

    def prepare_entitlement_wizard(self, cycle):
        wizard = self.env["spp.manual.entitlement.wizard"].create(
            {
                "cycle_id": cycle.id,
                "step": "step1",
                "cycle_membership_ids": [
                    (0, 0, {"partner_id": self.registrant_1.id, "entitlement_amount": 100, "selected": True})
                ],
            }
        )
        wizard.create_entitlement()
        return wizard

    def prepare_entitlement_wizard_for_manual(self, cycle):
        wizard = self.env["spp.manual.entitlement.wizard"].create(
            {
                "cycle_id": cycle.id,
                "step": "step1",
                "cycle_membership_ids": [
                    (0, 0, {"partner_id": self.registrant_1.id}),
                    (0, 0, {"partner_id": self.registrant_2.id}),
                ],
            }
        )
        return wizard

    def test_02_prepare_entitlement_manual(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard(cycle)
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_1.id), "Correct value")

    def test_03_cycle_prepare_entitlement(self):
        cycle = self.set_cycle()
        prepare_wizard = cycle.prepare_entitlement_manual()
        self.assertEqual(prepare_wizard["res_model"], "spp.manual.entitlement.wizard")

    def test_04_cycle_prepare_entitlement_existing(self):
        cycle = self.set_cycle()
        self.prepare_entitlement_wizard(cycle)
        prepare_wizard = cycle.prepare_entitlement_manual()
        prepare_wizard = self.env["spp.manual.entitlement.wizard"].browse(prepare_wizard["res_id"])
        self.assertEqual(len(prepare_wizard.cycle_membership_ids), 1)

    def test_05_cycle_manager_prepare_async(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard(cycle)
        wizard_vals = []
        wizard_count = 0
        while wizard_count <= 200:
            wizard_vals.append((0, 0, {"partner_id": self.registrant_1.id, "entitlement_amount": 100}))
            wizard_count += 1
        wizard.write({"cycle_membership_ids": wizard_vals})
        cycle_manager = self.env["g2p.cycle.manager.default"].search([("program_id", "=", self.program.id)])
        cycle_manager.prepare_manual_entitlements(cycle, wizard.cycle_membership_ids)
        self.assertEqual(cycle.locked, True)
        self.assertEqual(cycle.locked_reason, _("Prepare entitlement for beneficiaries."))

    def test_06_entitlement_wizard_wrong_file(self):
        pdf_file = None
        pdf_file_name = None

        file_path = self.get_file_path_3()
        with open(file_path, "rb") as f:
            pdf_file_name = f.name
            pdf_file = base64.b64encode(f.read())

        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard_for_manual(cycle)
        wizard.write({"file": pdf_file, "filename": pdf_file_name})
        with self.assertRaisesRegex(UserError, _("Only Excel and CSV files are allowed!")):
            wizard.file_change()

    def test_07_entitlement_wizard_xlsx(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard_for_manual(cycle)
        wizard.step_upload_csv()
        self.assertEqual(wizard.step, "step2b_1")

        xls_file = None
        xls_file_name = None

        file_path = self.get_file_path_1()
        with open(file_path, "rb") as f:
            xls_file_name = f.name
            xls_file = base64.b64encode(f.read())

        wizard.write({"file": xls_file, "filename": xls_file_name})
        wizard.start_import()
        self.assertEqual(len(wizard.upload_cycle_membership_ids), 2)

        wizard.finalize_import()
        self.assertEqual(wizard.step, "step3")

        wizard.create_entitlement()
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_1.id), "Correct value")
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_2.id), "Correct value")

    def test_08_entitlement_wizard_csv(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard_for_manual(cycle)
        wizard.step_upload_csv()
        self.assertEqual(wizard.step, "step2b_1")

        csv_file = None
        csv_file_name = None

        file_path = self.get_file_path_2()
        with open(file_path, "rb") as f:
            csv_file_name = f.name
            csv_file = base64.b64encode(f.read())

        wizard.write({"file": csv_file, "filename": csv_file_name})
        wizard.start_import()
        self.assertEqual(len(wizard.upload_cycle_membership_ids), 2)

        wizard.finalize_import()
        self.assertEqual(wizard.step, "step3")

        wizard.create_entitlement()
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_1.id), "Correct value")
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_2.id), "Correct value")

    def test_09_manual_add_entitlements(self):
        cycle = self.set_cycle()
        wizard = self.prepare_entitlement_wizard_for_manual(cycle)
        wizard.step_manual_select()
        self.assertEqual(wizard.step, "step2a")

        wizard.cycle_membership_ids[0].selected = True
        wizard.cycle_membership_ids[1].selected = True
        wizard.step_input_entitlement_amounts()
        self.assertEqual(wizard.step, "step3")

        wizard.create_entitlement()
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_1.id), "Correct value")
        self.assertTrue(wizard.search_existing_entitlement(self.registrant_2.id), "Correct value")
