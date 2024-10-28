from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestSPPDMSDirectory(TransactionCase):
    def setUp(self):
        super().setUp()
        self.directory = self.env["spp.dms.directory"].create(
            {
                "name": "Test Directory",
                "is_root_directory": True,
            }
        )

    def test_compute_complete_name_with_parent(self):
        child_directory = self.env["spp.dms.directory"].create(
            {
                "name": "Child Directory",
                "parent_id": self.directory.id,
            }
        )
        self.assertEqual(child_directory.complete_name, "Test Directory / Child Directory")

    def test_compute_complete_name_without_parent(self):
        self.assertEqual(self.directory.complete_name, "Test Directory")

    def test_compute_parent_id_for_non_root_directory(self):
        child_directory = self.env["spp.dms.directory"].create(
            {
                "name": "Child Directory",
                "parent_id": self.directory.id,
            }
        )
        self.assertEqual(child_directory.parent_id, self.directory)

    def test_compute_root_id_for_root_directory(self):
        self.assertEqual(self.directory.root_directory_id, self.directory)

    def test_compute_root_id_for_non_root_directory(self):
        child_directory = self.env["spp.dms.directory"].create(
            {
                "name": "Child Directory",
                "parent_id": self.directory.id,
            }
        )
        self.assertEqual(child_directory.root_directory_id, self.directory)

    def test_compute_size_with_files(self):
        # Create files to test size computation
        file1 = self.env["spp.dms.file"].create({"name": "File1", "directory_id": self.directory.id, "size": 1024})
        file2 = self.env["spp.dms.file"].create({"name": "File2", "directory_id": self.directory.id, "size": 2048})
        self.directory._compute_size()
        self.assertEqual(self.directory.size, file1.size + file2.size)

    def test_compute_size_with_mocking(self):
        with patch("odoo.addons.spp_dms.models.dms_file.SPPDMSFile.search_read", return_value=[{"size": 512}]):
            self.directory._compute_size()
            self.assertEqual(self.directory.size, 512)

    def test_compute_human_size(self):
        self.assertEqual(self.directory.human_size, False)

    def test_compute_count_directories(self):
        self.assertEqual(self.directory.count_directories, 0)

    def test_compute_count_files(self):
        self.assertEqual(self.directory.count_files, 0)

    def test_compute_count_elements(self):
        self.assertEqual(self.directory.count_elements, 0)

    def test_action_spp_dms_directories_all_directory(self):
        action = self.directory.action_spp_dms_directories_all_directory()
        self.assertEqual(action["context"]["default_parent_id"], self.directory.id)

    def test_action_spp_dms_files_all_directory(self):
        action = self.directory.action_spp_dms_files_all_directory()
        self.assertEqual(action["context"]["default_directory_id"], self.directory.id)
