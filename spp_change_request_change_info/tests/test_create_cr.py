import base64
import os

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class ChangeRequestChangeInfoTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.individual = cls.env["res.partner"].create(
            {
                "name": "Test Individual",
                "is_registrant": True,
                "is_group": False,
            }
        )
        cls.change_request = cls.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.change.info",
                "registrant_id": cls.individual.id,
                "applicant_id": cls.individual.id,
                "applicant_phone": "09123456789",
            }
        )
        cls.change_request.create_request_detail_no_redirect()
        cls.res_id = cls.env["spp.change.request.change.info"].search(
            [("id", "=", cls.change_request.request_type_ref_id.id)]
        )

        group_hq = [
            Command.link(cls.env.ref("spp_change_request.group_spp_change_request_validator").id),
            Command.link(cls.env.ref("spp_change_request.group_spp_change_request_hq_validator").id),
            Command.link(cls.env.ref("base.group_user").id),
        ]
        group_local = [
            Command.link(cls.env.ref("spp_change_request.group_spp_change_request_validator").id),
            Command.link(cls.env.ref("spp_change_request.group_spp_change_request_local_validator").id),
            Command.link(cls.env.ref("base.group_user").id),
        ]
        cls.cr_validator_local = cls.env["res.users"].create(
            {"name": "Validator Local", "login": "validator@local", "groups_id": group_local}
        )
        cls.cr_validator_hq = cls.env["res.users"].create(
            {"name": "Validator HQ", "login": "Validator@hq", "groups_id": group_hq}
        )

    def test_01_validate_cr_without_attachments(self):
        self.res_id.write({"family_name": "Test"})
        with self.assertRaisesRegex(ValidationError, "The required document Change Info Request Form is missing."):
            self.res_id.action_submit()

    def test_02_validate_cr_with_complete_data(self):
        self.res_id.write(
            {
                "family_name": "Test",
                "given_name": "Test",
            }
        )
        file = None
        filename = None
        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_document.jpeg"
        with open(file_path, "rb") as f:
            filename = f.name
            file = base64.b64encode(f.read())

        vals = {
            "content": file,
            "name": filename,
            "category_id": self.env.ref("spp_change_request_change_info.spp_dms_change_info").id,
            "directory_id": self.res_id.dms_directory_ids[0].id,
            "change_request_change_info_id": self.res_id.id,
        }
        self.env["spp.dms.file"].create(vals)
        self.res_id.action_submit()

        self.assertEqual(
            self.change_request.state,
            "pending",
            "CR should now be in Pending Validation!",
        )
        self.res_id.with_user(self.cr_validator_local.id).action_validate()
        self.res_id.with_user(self.cr_validator_hq.id).action_validate()
        self.assertEqual(
            self.change_request.state,
            "applied",
            "CR should now be in Applied!",
        )
