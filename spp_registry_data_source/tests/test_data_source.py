from odoo.tests.common import TransactionCase


class TestDataSource(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.data_source = cls.env["spp.data.source"].create(
            {
                "name": "Test Data Source",
                "url": "https://test.com",
                "auth_type": "basic_authentication",
            }
        )

        cls.source_path = cls.env["spp.data.source.path"].create(
            {
                "data_source_id": cls.data_source.id,
                "key": "test_path",
                "value": "/test",
            }
        )

        cls.field_mapping = cls.env["spp.data.source.field.mapping"].create(
            {
                "data_source_id": cls.data_source.id,
                "key": "test_field",
                "value": "test_value",
            }
        )

        cls.parameter = cls.env["spp.data.source.parameter"].create(
            {
                "data_source_id": cls.data_source.id,
                "key": "test_param",
                "value": "test_value",
            }
        )

    def test_get_field_mapping_key_value_pair(self):
        self.assertEqual(
            self.data_source.get_field_mapping_key_value_pair(),
            {"test_field": "test_value"},
        )

    def test_get_parameter_key_value_pair(self):
        self.assertEqual(
            self.data_source.get_parameter_key_value_pair(),
            {"test_param": "test_value"},
        )

    def test_get_source_path_id_key_full_path_pair(self):
        self.assertEqual(
            self.data_source.get_source_path_id_key_full_path_pair(),
            {"test_path": "https://test.com/test"},
        )
