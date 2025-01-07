from odoo.tests import TransactionCase


class TestDmsDirectory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.dms_directory_model = cls.env["spp.dms.directory"]
        cls.dms_directry_id = cls.dms_directory_model.create({"name": "Test Directory"})

        cls.dms_directry_parent_id = cls.dms_directory_model.create({"name": "Parent Directory"})
        cls.dms_directory_with_parent_id = cls.dms_directory_model.create(
            {"name": "Child Directory", "parent_id": cls.dms_directry_parent_id.id}
        )

    def test_default_parent_id(self):
        parent_id = self.dms_directory_model.with_context(
            active_model="spp.dms.directory", active_id=1
        )._default_parent_id()
        self.assertEqual(parent_id, 1)

        parent_id = self.dms_directory_model.with_context(active_id=False)._default_parent_id()
        self.assertFalse(parent_id)

    def test_compute_complete_name(self):
        self.dms_directry_id._compute_complete_name()
        self.assertEqual(self.dms_directry_id.complete_name, "Test Directory")

        self.dms_directory_with_parent_id._compute_complete_name()
        self.assertEqual(self.dms_directory_with_parent_id.complete_name, "Parent Directory / Child Directory")

    def test_compute_size(self):
        new_dms = self.dms_directory_model.new({"name": "New Directory"})
        new_dms._compute_size()
        self.assertEqual(new_dms.size, 0)

        self.dms_directry_id._compute_size()
        self.assertEqual(self.dms_directry_id.size, 0)

    def test_compute_human_size(self):
        self.dms_directry_id.size = 1024
        self.dms_directry_id._compute_human_size()
        self.assertEqual(self.dms_directry_id.human_size, "1.00 Kb")

    def test_compute_count_directories(self):
        self.dms_directory_with_parent_id._compute_count_directories()
        self.assertEqual(self.dms_directory_with_parent_id.count_directories, 0)
        self.assertEqual(self.dms_directory_with_parent_id.count_directories_title, "0 Subdirectories")

    def test_compute_count_files(self):
        self.dms_directory_with_parent_id._compute_count_files()
        self.assertEqual(self.dms_directory_with_parent_id.count_files, 0)
        self.assertEqual(self.dms_directory_with_parent_id.count_files_title, "0 Files")

    def test_compute_count_elements(self):
        self.dms_directory_with_parent_id._compute_count_elements()
        self.assertEqual(self.dms_directory_with_parent_id.count_elements, 0)

    def test_compute_count_total_directories(self):
        self.dms_directory_with_parent_id._compute_count_total_directories()
        self.assertEqual(self.dms_directory_with_parent_id.count_total_directories, 0)

    def test_compute_count_total_files(self):
        self.dms_directory_with_parent_id._compute_count_total_files()
        self.assertEqual(self.dms_directory_with_parent_id.count_total_files, 0)

    def test_action_spp_dms_directories_all_directory(self):
        action = self.dms_directry_id.action_spp_dms_directories_all_directory()

        self.assertEqual(action["res_model"], "spp.dms.directory")
        self.assertEqual(action["target"], "current")
        self.assertEqual(action["view_mode"], "tree,form")
        self.assertEqual(action["context"]["default_parent_id"], self.dms_directry_id.id)
        self.assertEqual(action["context"]["searchpanel_default_parent_id"], self.dms_directry_id.id)
        self.assertEqual(action["domain"], [("parent_id", "child_of", self.dms_directry_id.id)])
        self.assertEqual(action["limit"], 80)
        self.assertFalse(action["res_id"])
        self.assertFalse(action["view_id"])
        self.assertFalse(action["groups_id"])
        self.assertFalse(action["search_view_id"])
        self.assertFalse(action["filter"])

    def test_action_spp_dms_files_all_directory(self):
        action = self.dms_directry_id.action_spp_dms_files_all_directory()

        self.assertEqual(action["res_model"], "spp.dms.file")
        self.assertEqual(action["target"], "current")
        self.assertEqual(action["view_mode"], "tree,form")
        self.assertEqual(action["context"]["default_directory_id"], self.dms_directry_id.id)
        self.assertEqual(action["context"]["searchpanel_default_directory_id"], self.dms_directry_id.id)
        self.assertEqual(action["domain"], [("directory_id", "child_of", self.dms_directry_id.id)])
        self.assertEqual(action["limit"], 80)
        self.assertFalse(action["res_id"])
        self.assertFalse(action["view_id"])
        self.assertFalse(action["groups_id"])
        self.assertFalse(action["search_view_id"])
