from odoo.exceptions import ValidationError

from . import common


class TestG2pProgramCreateWiz(common.Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test = cls.program_create_wizard({})

    def test_01_create_program_without_compliance_manager(self):
        self._test._check_compliance_manager_info()
        action = self._test.create_program()
        program = self.env["g2p.program"].browse(action["res_id"])
        self.assertFalse(
            bool(program.compliance_managers),
            "Should not create compliance manager for new program!",
        )

    def test_02_create_program_errors(self):
        self._test.compliance_criteria = True
        self._test.compliance_kind = None
        error = "^Not enough information for creating compliance manager!$"
        with self.assertRaisesRegex(ValidationError, error):
            self._test.create_program()
        self._test.compliance_kind = "g2p.program_membership.manager.default"
        self._test.compliance_domain = None
        with self.assertRaisesRegex(ValidationError, error):
            self._test.create_program()

    def test_03_create_program_default_compliance_manager(self):
        self._test.write(
            {
                "compliance_criteria": True,
                "compliance_kind": "g2p.program_membership.manager.default",
                "compliance_domain": "[['id', '>', 2]]",
            }
        )
        action = self._test.create_program()
        program = self.env["g2p.program"].browse(action["res_id"])
        self.assertTrue(
            bool(program.compliance_managers),
            "Should create compliance manager for new program!",
        )
        manager = program.compliance_managers[0].manager_ref_id
        self.assertEqual(
            manager._name,
            "g2p.program_membership.manager.default",
            "Manager should be correct!",
        )
        self.assertEqual(manager.eligibility_domain, "[['id', '>', 2]]", "Manager should be correct!")
        self.assertEqual(manager.program_id, program, "Manager should be correct!")
