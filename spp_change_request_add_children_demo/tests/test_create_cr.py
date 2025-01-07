import base64
import os

from odoo import Command, _
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class ChangeRequestAddChildrenDemoTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = cls.env["res.partner"].create(
            {
                "name": "Test Group",
                "is_registrant": True,
                "is_group": True,
            }
        )

        cls.individual = cls.env["res.partner"].create(
            {
                "name": "Test Individual",
                "is_registrant": True,
                "is_group": False,
            }
        )

        cls.membership = cls.env["g2p.group.membership"].create(
            {
                "group": cls.group.id,
                "individual": cls.individual.id,
            }
        )

        cls.change_request = cls.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.add.children",
                "registrant_id": cls.group.id,
                "applicant_id": cls.individual.id,
                "applicant_phone": "09123456789",
            }
        )
        cls.change_request.create_request_detail_no_redirect()
        cls.res_id = cls.env["spp.change.request.add.children"].search(
            [("id", "=", cls.change_request.request_type_ref_id.id)]
        )

        group_hq = [
            Command.link(cls.env.ref("spp_change_request.group_spp_change_request_validator").id),
            Command.link(cls.env.ref("spp_change_request.group_spp_change_request_hq_validator").id),
            Command.link(cls.env.ref("g2p_registry_base.group_g2p_admin").id),
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

    def get_vals(self):
        if not self.env["gender.type"].search([]):
            gender = self.env["gender.type"].create({"code": "M", "value": "Male"})
        else:
            gender = self.env["gender.type"].search([])[0]

        return {
            "full_name": "Test Child",
            "family_name": "Child",
            "given_name": "Test",
            "addl_name": "Jr",
            "applicant_relation": "mother",
            "birth_place": "Hometown",
            "birthdate_not_exact": True,
            "birthdate": "1990-01-01",
            "gender": gender.value,
            "phone": "09123456789",
            "uid_number": "123456789125",
        }

    def test_01_validate_cr_without_attachments(self):
        vals = self.get_vals()
        self.res_id.write(vals)
        with self.assertRaisesRegex(ValidationError, "The required document Add Children Request Form is missing."):
            self.res_id.action_submit()

    def test_02_validate_cr_with_complete_data(self):
        vals = self.get_vals()
        self.res_id.write(vals)
        file = None
        filename = None
        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_document.jpeg"
        with open(file_path, "rb") as f:
            filename = f.name
            file = base64.b64encode(f.read())

        vals = {
            "content": file,
            "name": filename,
            "category_id": self.env.ref("spp_change_request_add_children_demo.spp_dms_add_children").id,
            "directory_id": self.res_id.dms_directory_ids[0].id,
            "change_request_add_children_id": self.res_id.id,
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
        open_form = self.res_id.open_registrant_details_form()
        self.assertEqual(
            open_form["name"],
            _("Group Details"),
            "Incorrect Name!",
        )

    def test_03_validate_cr_with_invalid_data(self):
        reg_vals = {
            "birth_place": "Hometown",
            "phone": "09123456789",
            "uid_number": "123456789125",
        }
        self.res_id.write(reg_vals)

        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_document.jpeg"
        with open(file_path, "rb") as f:
            filename = f.name
            file = base64.b64encode(f.read())

        vals = {
            "content": file,
            "name": filename,
            "category_id": self.env.ref("spp_change_request_add_children_demo.spp_dms_add_children").id,
            "directory_id": self.res_id.dms_directory_ids[0].id,
            "change_request_add_children_id": self.res_id.id,
        }
        self.env["spp.dms.file"].create(vals)
        error_message = [
            _("The Family Name is required!"),
            _("The First Name is required!"),
            _("The Date of Birth is required!"),
            _("The Relationship to Applicant is required!"),
            _("The Gender is required!"),
        ]
        error_message = "\n".join(error_message)
        with self.assertRaisesRegex(ValidationError, error_message):
            self.res_id.validate_data()

    def test_04_update_live_data_with_kinds(self):
        vals = self.get_vals()
        kind = self.env.ref("g2p_registry_membership.group_membership_kind_head").id
        vals["kind"] = [(6, 0, [kind])]
        self.res_id.write(vals)
        file = None
        filename = None
        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_document.jpeg"
        with open(file_path, "rb") as f:
            filename = f.name
            file = base64.b64encode(f.read())

        vals = {
            "content": file,
            "name": filename,
            "category_id": self.env.ref("spp_change_request_add_children_demo.spp_dms_add_children").id,
            "directory_id": self.res_id.dms_directory_ids[0].id,
            "change_request_add_children_id": self.res_id.id,
        }
        self.env["spp.dms.file"].create(vals)
        self.res_id.update_live_data()

        individual_id = self.env["g2p.group.membership"].search([("group", "=", self.group.id), ("kind", "in", kind)])
        self.assertTrue(individual_id, "Individual not found!")

    def test_05_update_live_data_without_phone_uid(self):
        vals = self.get_vals()
        vals.pop("phone")
        vals.pop("uid_number")

        self.res_id.write(vals)
        file = None
        filename = None
        file_path = f"{os.path.dirname(os.path.abspath(__file__))}/sample_document.jpeg"
        with open(file_path, "rb") as f:
            filename = f.name
            file = base64.b64encode(f.read())

        vals = {
            "content": file,
            "name": filename,
            "category_id": self.env.ref("spp_change_request_add_children_demo.spp_dms_add_children").id,
            "directory_id": self.res_id.dms_directory_ids[0].id,
            "change_request_add_children_id": self.res_id.id,
        }
        self.env["spp.dms.file"].create(vals)
        self.res_id.update_live_data()

        individual_id = self.env["res.partner"].search([("name", "=", "Test Child")])
        self.assertFalse(individual_id.phone_number_ids, "Should not have phone number!")
        self.assertFalse(individual_id.reg_ids, "Should not have registrant ID!")

    def test_06_create_request_detail_demo(self):
        change_request = self.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.add.children",
                "registrant_id": self.group.id,
                "applicant_id": self.individual.id,
                "applicant_phone": "09123456789",
            }
        )
        change_request.create_request_detail_demo()
        self.assertTrue(change_request.request_type_ref_id, "Request Type Reference ID not set!")
