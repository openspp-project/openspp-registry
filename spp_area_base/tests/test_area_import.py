import logging

from odoo.exceptions import ValidationError

from .common import AreaImportBaseTestMixin

_logger = logging.getLogger(__name__)


class BaseAreaImportTest(AreaImportBaseTestMixin):
    def test_01_cancel_area_import(self):
        self.area_import_id.cancel_import()

        self.assertEqual(self.area_import_id.state, "Cancelled")

    def test_02_reset_to_uploaded_area(self):
        self.area_import_id.reset_to_uploaded()

        self.assertEqual(self.area_import_id.state, "Uploaded")

    def test_03_import_area_data(self):
        with self.assertRaises(ValidationError):
            self.area_import_id.import_data()

        lang = self.env["res.lang"].with_context(active_test=False).search([("iso_code", "=", "ar")])
        lang.active = True

        self.area_import_id.import_data()
        raw_data_ids = self.area_import_id.raw_data_ids

        self.assertEqual(len(raw_data_ids.ids), self.area_import_id.tot_rows_imported)
        self.assertEqual(0, self.area_import_id.tot_rows_error)
        self.assertEqual(self.area_import_id.state, "Uploaded")
        self.assertEqual(
            len(self.env["spp.area.import.raw"].search([("id", "in", raw_data_ids.ids), ("state", "=", "New")])),
            self.area_import_id.tot_rows_imported,
        )

    def test_06_reload_page(self):
        action = self.area_import_id.refresh_page()

        self.assertEqual(
            action,
            {
                "type": "ir.actions.client",
                "tag": "reload",
            },
        )

    def test_07_async_mark_import_done(self):
        self.area_import_id._async_mark_done()

        self.assertFalse(self.area_import_id.locked)
        self.assertFalse(self.area_import_id.locked_reason)
