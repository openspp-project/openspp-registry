from odoo.tests import TransactionCase

from ..tools import file_tools


class TestFileTools(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_check_name(self):
        name = "test"
        self.assertTrue(file_tools.check_name(name))

        name = "/invalid/name/with/slashes"
        self.assertFalse(file_tools.check_name(name))

    def test_compute_name(self):
        name = "test.py"
        suffix = 1
        escape_suffix = False
        self.assertEqual(file_tools.compute_name(name, suffix, escape_suffix), "test.py(1)")

        escape_suffix = True
        self.assertEqual(file_tools.compute_name(name, suffix, escape_suffix), "test(1).py")

    def test_unique_name(self):
        names = ["test.py", "test(1).py"]
        name = "test(2).py"
        result = file_tools.unique_name(name, names)
        self.assertEqual(result, "test(2).py")

        name = "test.py"
        result = file_tools.unique_name(name, names)
        self.assertEqual(result, "test.py(1)")
