from unittest.mock import patch

from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_individual_1 = cls._create_registrant({"name": "Liu Bei"})
        cls._test_individual_2 = cls._create_registrant({"name": "Guan Yu"})
        cls._test_individual_3 = cls._create_registrant({"name": "Zhang Fei"})
        cls._test_group = cls._create_registrant(
            {
                "name": "Shu clan",
                "is_group": True,
                "group_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "individual": cls._test_individual_1.id,
                            "kind": [
                                (
                                    4,
                                    cls.env.ref("g2p_registry_membership.group_membership_kind_head").id,
                                )
                            ],
                        },
                    ),
                    (0, 0, {"individual": cls._test_individual_2.id}),
                    (0, 0, {"individual": cls._test_individual_3.id}),
                ],
            }
        )

    @classmethod
    def _create_registrant(cls, vals):
        cls.assertTrue(isinstance(vals, dict), "Return vals should be a dict!")
        vals.update({"is_registrant": True})
        return cls.env["res.partner"].create(vals)

    @classmethod
    @patch("odoo.addons.spp_change_request.models.change_request.ChangeRequestBase._selection_request_type_ref_id")
    def _create_change_request(self, mock_request_type_selection):
        mock_request_type_selection.return_value = [("test.request.type", "Test Request Type")]
        mock_request_type_selection.__name__ = "_mocked__selection_request_type_ref_id"
        return self.env["spp.change.request"].create(
            {
                "name": "Test Request",
                "request_type": "test.request.type",
            }
        )
