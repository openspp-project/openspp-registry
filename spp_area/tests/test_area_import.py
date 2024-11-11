import logging

from .common import AreaImportTestMixin

_logger = logging.getLogger(__name__)


class AreaImportTest(AreaImportTestMixin):
    def test_01_cancel_import(self):
        self.area_import_id.cancel_import()

        self.assertEqual(self.area_import_id.state, "Cancelled")

    def test_02_reset_to_uploaded(self):
        self.area_import_id.reset_to_uploaded()

        self.assertEqual(self.area_import_id.state, "Uploaded")

    def test_03_import_data(self):
        self.area_import_id.import_data()

        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Imported")
        self.assertEqual(
            len(self.env["spp.area.import.raw"].search([("id", "in", raw_data_ids.ids), ("state", "=", "New")])),
            self.area_import_id.tot_rows_imported,
        )

    def test_04_validate_raw_data(self):
        # Greater than or equal to 400 rows
        self.area_import_id.import_data()
        self.area_import_id.validate_raw_data()

        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Imported")
        self.assertTrue(self.area_import_id.locked)
        self.assertEqual(self.area_import_id.locked_reason, "Validating data.")

        # Less than 400 rows
        self.area_import_id_2.import_data()
        self.area_import_id_2.validate_raw_data()

        raw_data_ids = self.area_import_id_2.raw_data_ids
        self.assertEqual(len(raw_data_ids.ids), self.area_import_id_2.tot_rows_imported)
        self.assertEqual(0, self.area_import_id_2.tot_rows_error)
        self.assertEqual(self.area_import_id_2.state, "Validated")
        self.assertFalse(self.area_import_id_2.locked)
        self.assertFalse(self.area_import_id_2.locked_reason)
        self.assertEqual(
            len(
                self.env["spp.area.import.raw"].search(
                    [("id", "in", raw_data_ids.ids), ("state", "=", "Validated")],
                )
            ),
            self.area_import_id_2.tot_rows_imported,
        )

    def test_05_save_to_area(self):
        # Greater than or equal to 400 rows
        self.area_import_id.import_data()
        self.area_import_id.save_to_area()

        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Imported")
        self.assertTrue(self.area_import_id.locked)
        self.assertEqual(self.area_import_id.locked_reason, "Saving to Area.")

        # Less than 400 rows
        self.area_import_id_2.import_data()
        self.area_import_id_2.validate_raw_data()
        self.area_import_id_2.save_to_area()

        raw_data_ids = self.area_import_id_2.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id_2.tot_rows_imported)
        self.assertEqual(0, self.area_import_id_2.tot_rows_error)
        self.assertEqual(self.area_import_id_2.state, "Done")
        self.assertFalse(self.area_import_id_2.locked)
        self.assertFalse(self.area_import_id_2.locked_reason)

        for raw_data_id in raw_data_ids:
            self.assertTrue(
                bool(
                    self.env["spp.area"].search(
                        [
                            ("draft_name", "=", raw_data_id.admin_name),
                            ("code", "=", raw_data_id.admin_code),
                        ],
                        limit=1,
                    )
                )
            )

    def test_06_refresh_page(self):
        action = self.area_import_id.refresh_page()

        self.assertEqual(
            action,
            {
                "type": "ir.actions.client",
                "tag": "reload",
            },
        )

    def test_07_async_mark_done(self):
        self.area_import_id._async_mark_done()

        self.assertFalse(self.area_import_id.locked)
        self.assertFalse(self.area_import_id.locked_reason)
