# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.

import logging

# from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


# @tagged("post_install", "-at_install")
class AreaTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Initial Setup of Variables
        cls.area_1 = cls.env["spp.area"].create(
            {
                "draft_name": "Testing Area",
            }
        )
        cls.area_1_child = cls.env["spp.area"].create(
            {
                "draft_name": "Testing Area Child",
                "parent_id": cls.area_1.id,
            }
        )

    def test_01_check_childs(self):
        self.area_1._compute_get_childs()

        self.assertEqual(len(self.area_1.child_ids), 1)
