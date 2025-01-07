import logging
import os

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase

_logger = logging.getLogger(__name__)

OPTIONS = {
    "import_skip_records": [],
    "import_set_empty_fields": [],
    "fallback_values": {},
    "name_create_enabled_fields": {},
    "encoding": "ascii",
    "separator": ",",
    "quoting": '"',
    "date_format": "",
    "datetime_format": "",
    "float_thousand_separator": ",",
    "float_decimal_separator": ".",
    "advanced": True,
    "has_headers": True,
    "keep_matches": False,
    "limit": 2000,
    "sheets": [],
    "sheet": "",
    "skip": 0,
    "tracking_disable": True,
}


class TestResPartnerImportMatch(TransactionCase):
    @staticmethod
    def get_file_path_1():
        return f"{os.path.dirname(os.path.abspath(__file__))}/res_partner_group_name.csv"

    @staticmethod
    def get_file_path_2():
        return f"{os.path.dirname(os.path.abspath(__file__))}/res_partner_name.csv"

    @staticmethod
    def get_file_path_3():
        return f"{os.path.dirname(os.path.abspath(__file__))}/res_partner_group_async.csv"

    def setUp(self):
        super().setUp()
        self._test_hh = self.env["res.partner"].create(
            {
                "name": "Renaud",
                "is_registrant": True,
                "is_group": True,
                "email": "renaud@gmail.com",
            }
        )
        self._test_applicant = self.env["res.partner"].create(
            {
                "name": "Rufino Renaud",
                "family_name": "Rufino",
                "given_name": "Renaud",
                "is_group": False,
                "is_registrant": True,
                "phone": "+639266716911",
                "email": "rufinorenaud12@gmail.com",
            }
        )

    def _base_import_record(self, res_model, file_path):
        with open(file_path, encoding="utf-8") as f:
            csv_file = str.encode(f.read(), "utf-8")
            csv_file_name = f.name

        base_import = self.env["base_import.import"].create(
            {
                "res_model": res_model,
                "file": csv_file,
                "file_name": csv_file_name,
                "file_type": "csv",
            }
        )
        return base_import

    def create_matching_given_family_name(self):
        res_partner = self.env["ir.model"].search([("model", "=", "res.partner")])
        vals = {"model_id": res_partner.id, "overwrite_match": True}
        import_match = self.env["spp.import.match"].create(vals)
        given_name_field = self.env["ir.model.fields"].search(
            [("name", "=", "given_name"), ("model_id", "=", res_partner.id)]
        )

        self.env["spp.import.match.fields"].create({"field_id": given_name_field.id, "match_id": import_match.id})

        family_name_field = self.env["ir.model.fields"].search(
            [("name", "=", "family_name"), ("model_id", "=", res_partner.id)]
        )

        self.env["spp.import.match.fields"].create({"field_id": family_name_field.id, "match_id": import_match.id})

        return import_match

    def create_matching_name(self):
        res_partner = self.env["ir.model"].search([("model", "=", "res.partner")])
        vals = {"model_id": res_partner.id, "overwrite_match": True}
        import_match = self.env["spp.import.match"].create(vals)
        name_field = self.env["ir.model.fields"].search([("name", "=", "name"), ("model_id", "=", res_partner.id)])

        self.env["spp.import.match.fields"].create({"field_id": name_field.id, "match_id": import_match.id})

        return import_match

    def test_01_res_partner_change_email_by_name(self):
        """Change email based on given_name, family_name."""
        self.create_matching_given_family_name()
        file_path = self.get_file_path_2()
        record = self._base_import_record("res.partner", file_path)
        record.execute_import(["given_name", "family_name", "name", "email"], [], OPTIONS)

        self._test_applicant.env.cache.invalidate()
        self.assertEqual(self._test_applicant.email, "rufinorenaud@gmail.com")

    def test_02_res_partner_change_email_by_group_name(self):
        """Change email based on name."""
        self.create_matching_name()
        file_path = self.get_file_path_1()
        record = self._base_import_record("res.partner", file_path)

        record.execute_import(["name", "email"], ["name", "email"], OPTIONS)
        self._test_hh.env.cache.invalidate()
        self.assertEqual(self._test_hh.email, "renaudhh@gmail.com")

    def test_03_res_partner_group_async(self):
        """Trigger Async."""
        file_path = self.get_file_path_3()
        record = self._base_import_record("res.partner", file_path)

        async_rec = record.execute_import(["name", "email"], ["name", "email"], OPTIONS)
        self._test_hh.env.cache.invalidate()
        self.assertEqual(async_rec["async"], True)

    def test_04_res_partner_group_async_dryrun(self):
        """Trigger Async."""
        file_path = self.get_file_path_3()
        record = self._base_import_record("res.partner", file_path)

        async_rec = record.execute_import(["name", "email"], ["name", "email"], OPTIONS, True)
        self._test_hh.env.cache.invalidate()
        self.assertTrue(async_rec, "Result should have value")

    def test_05_check_duplication_on_import_match_config(self):
        """Check duplication on import match config."""
        import_match = self.create_matching_name()
        with self.assertRaisesRegex(ValidationError, _("Field 'Name', already exists!")):
            import_match.write(
                {
                    "field_ids": [
                        (0, 0, {"field_id": import_match.field_ids[0].field_id.id, "match_id": import_match.id})
                    ]
                }
            )
            import_match.field_ids[0]._onchange_field_id()

        self.assertEqual(len(import_match.field_ids), 2)

    def test_06_test_match_find(self):
        """Test match find."""
        import_match = self.create_matching_name()
        import_match.field_ids[0].imported_value = "Rufin Renaud"
        import_match.field_ids[0].conditional = True
        result = import_match._match_find(
            import_match.model_id, {"name": "Rufino Renaud"}, {"name": "Rufino Renaud", "id": None}
        )

        self.assertEqual(result, import_match.model_id)
