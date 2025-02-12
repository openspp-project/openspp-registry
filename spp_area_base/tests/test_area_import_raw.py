from .common import AreaImportTestMixin


class AreaImportRawTest(AreaImportTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.area_import_raw_id = cls.env["spp.area.import.raw"].create(
            {
                "area_import_id": cls.area_import_id.id,
                "admin_name": "Philippines",
                "admin_code": "PH",
                "parent_name": "",
                "parent_code": "",
                "level": 0,
                "area_sqkm": "194000.23",
            }
        )

        cls.area_import_raw_child_id = cls.env["spp.area.import.raw"].create(
            {
                "area_import_id": cls.area_import_id.id,
                "admin_name": "Manila",
                "admin_code": "MNL",
                "parent_name": "Philippines",
                "parent_code": "PH",
                "level": 1,
                "area_sqkm": "200.23",
            }
        )

    def test_01_validate_raw_data_no_error(self):
        result = self.area_import_raw_id.validate_raw_data()
        result_child = self.area_import_raw_child_id.validate_raw_data()

        self.assertFalse(result)
        self.assertEqual(self.area_import_raw_id.state, "Validated")
        self.assertEqual(self.area_import_raw_id.remarks, "No Error")

        self.assertFalse(result_child)
        self.assertEqual(self.area_import_raw_child_id.state, "Validated")
        self.assertEqual(self.area_import_raw_child_id.remarks, "No Error")

    def test_02_validate_raw_data_with_error(self):
        self.area_import_raw_id.admin_name = ""
        self.area_import_raw_id.area_sqkm = "text"
        self.area_import_raw_id.parent_name = "MNL"
        self.area_import_raw_child_id.parent_name = ""

        self.area_import_raw_id.validate_raw_data()
        self.area_import_raw_child_id.validate_raw_data()

        self.assertEqual(self.area_import_raw_id.state, "Error")
        self.assertIn("Name and Code of area is required.", self.area_import_raw_id.remarks)
        self.assertIn("AREA_SQKM should be numerical.", self.area_import_raw_id.remarks)
        self.assertIn(
            "Level 0 area should not have a parent name and parent code.",
            self.area_import_raw_id.remarks,
        )

        self.assertEqual(self.area_import_raw_child_id.state, "Error")
        self.assertIn(
            "Level 1 and above area should have a parent name and parent code.",
            self.area_import_raw_child_id.remarks,
        )

    def test_03_save_to_area(self):
        self.area_import_raw_id.area_sqkm = ""

        self.area_import_raw_id.save_to_area()
        self.assertEqual(self.area_import_raw_id.state, "Posted")

        self.area_import_raw_id.save_to_area()
        self.assertEqual(self.area_import_raw_id.state, "Updated")
