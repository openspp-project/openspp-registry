from unittest.mock import patch

from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_individual_1 = cls._create_registrant({"name": "Liu Bei"})
        cls._test_individual_2 = cls._create_registrant({"name": "Guan Yu"})
        cls._test_individual_3 = cls._create_registrant({"name": "Zhang Fei"})

    @classmethod
    def _create_registrant(cls, vals):
        cls.assertTrue(isinstance(vals, dict), "Return vals should be a dict!")
        return cls.env["res.partner"].create(vals)

    @classmethod
    @patch("odoo.addons.spp_change_request_base.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def _create_change_request(self, mock_request_type_selection):
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        return self.env["spp.change.request"].create(
            {
                "name": "Test Request",
                "request_type": "test.request.type",
            }
        )
