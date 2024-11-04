# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPRegistrant(models.Model):
    _name = "res.partner"
    _inherit = [_name, "mail.thread"]

    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")
    image_1920_filename = fields.Char("Image 1920 FileName")

    def open_issue_idpass_wiz(self):
        """
        This opens the ID Pass Issuance Wizard
        """
        view = self.env.ref("spp_idpass.issue_id_pass_wizard_form_view")
        wiz = self.env["spp.issue.idpass.wizard"].create({"registrant_id": self.id})
        return {
            "name": _("Issue ID Pass"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.issue.idpass.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }

    def send_idpass_parameters(self, vals):  # noqa: C901
        """
        This function is being used to handle the passing of Datas
        to ID Pass, to generate the ID of the registrant
        :param vals: The Values.
        :return: Response from the API.
        """
        id_pass_param = self.env["spp.id.pass"].search([("is_active", "=", True)])
        if vals["idpass"]:
            id_pass_param = self.env["spp.id.pass"].search([("id", "=", vals["idpass"])])

        if id_pass_param:
            data_param = {
                "given_names": self.given_name,
                "identification_no": f"{self.id:06d}",
                "place_of_birth": self.birth_place or "",
                "sex": self.gender or "",
                "surname": self.family_name,
                "nationality": "",
            }
            profile_pic = self.image_1920 or False
            profile_pic_filename = self.image_1920_filename or False
            if self.is_group:
                head_id = 0
                for group_member in self.group_membership_ids:
                    for member_kind in group_member.kind:
                        if member_kind.is_unique:
                            head_id = group_member.individual.id
                            break
                    if head_id > 0:
                        break
                if head_id > 0:
                    head_registrant = self.env["res.partner"].search([("id", "=", head_id)])
                    data_param = {
                        "given_names": head_registrant.given_name,
                        "identification_no": f"{head_registrant.id:09d}",
                        "place_of_birth": head_registrant.birth_place or "",
                        "sex": head_registrant.gender or "",
                        "surname": head_registrant.family_name,
                        "nationality": "",
                    }
                    profile_pic = head_registrant.image_1920 or False
                    profile_pic_filename = head_registrant.image_1920_filename or False
                else:
                    raise ValidationError(_("ID PASS Error: No Head or Principal Recipient assigned to this Group"))  # noqa: C901

            issue_date = datetime.today().strftime("%Y/%m/%d")
            expiry_date = datetime.today()

            if id_pass_param[0].expiry_length_type == "years":
                expiry_date = datetime.today() + relativedelta(years=id_pass_param[0].expiry_length)
            elif id_pass_param[0].expiry_length_type == "months":
                expiry_date = datetime.today() + relativedelta(months=id_pass_param[0].expiry_length)
            else:
                expiry_date = datetime.today() + relativedelta(days=id_pass_param[0].expiry_length)
            expiry_date = expiry_date.strftime("%Y/%m/%d")
            data_param.update(
                {
                    "date_of_expiry": expiry_date,
                    "date_of_issue": issue_date,
                }
            )
            file_type = ""
            if profile_pic_filename:
                file_type = profile_pic_filename.partition(".")[2]
                if file_type == "jpg":
                    file_type = "jpeg"
            else:
                if profile_pic:
                    raise ValidationError(_("ID PASS Error: Please try reuploading the ID Picture"))  # noqa: C901

            profile_pic_url = ""
            if profile_pic and file_type in ("jpeg", "png"):
                profile_pic = str(profile_pic)
                profile_pic = profile_pic[2:]
                profile_pic_url = "data:image/" + file_type + ";base64," + profile_pic

                data_param.update(
                    {
                        "profile_svg_6": profile_pic_url,
                    }
                )
            data_param.update(
                {
                    "qrcode_svg_1": f"{data_param['identification_no']};"
                    f"{data_param['given_names']};{data_param['surname']}"
                }
            )

            data = {"fields": data_param}

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = self.send_idpass_data(
                id_pass_param[0].api_url,
                json.dumps(data),
                headers,
                (id_pass_param[0].api_username, id_pass_param[0].api_password),
            )

            if response.status_code == 200:
                pdf_vals = response.json()
                file_pdf = pdf_vals["files"]["pdf"]
                file_pdf = file_pdf[28:]
                file_pdf_filename = "{}_{}_{}.pdf".format(
                    id_pass_param[0].filename_prefix,
                    data_param["identification_no"],
                    datetime.today().strftime("%Y-%m-%d"),
                )
                self.id_pdf = file_pdf
                self.id_pdf_filename = file_pdf_filename

                idqueue = self.env["spp.print.queue.id"].search([("id", "=", vals["id_queue"])])
                idqueue.id_pdf = self.id_pdf
                idqueue.id_pdf_filename = self.id_pdf_filename

                self.check_existing_id(data_param["identification_no"])

                return
            else:
                raise ValidationError(
                    _("ID PASS Error: %(reason)s Code: %(code)s")
                    % {"reason": response.reason, "code": response.status_code}
                )  # noqa: C901
            return
        else:
            raise ValidationError(_("ID Pass Error: No API set"))  # noqa: C901

    def send_idpass_data(self, url, data, headers, auth):
        """
        This sends a request to generate the ID using default authentication
        :param url: The URL.
        :param data: The Data.
        :param headers: The Headers.
        :param auth: The Authentication.
        :return: Request API to send data and receive a response.
        """

        return requests.post(
            url,
            data=data,
            headers=headers,
            auth=auth,
            timeout=10,  # Adding a timeout of 10 seconds
        )

    def check_existing_id(self, identification_no):
        """
        This checks if the ID already exists in the registrant g2p.reg.id
        if yes create else update
        :param identification_no: The Identification Number.
        :return: Write or update the reg_ids depending on condition.
        """
        existing_id = self.env["g2p.reg.id"].search(
            [
                ("partner_id", "=", self.id),
                ("id_type", "=", self.env.ref("spp_idpass.id_type_idpass").id),
            ]
        )

        if existing_id:
            self.update(
                {
                    "reg_ids": [
                        (
                            1,
                            existing_id[0].id,
                            {
                                "id_type": existing_id[0].id_type.id,
                                "value": identification_no,
                            },
                        )
                    ]
                }
            )
        else:
            self.write(
                {
                    "reg_ids": [
                        (
                            0,
                            0,
                            {
                                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
                                "value": identification_no,
                            },
                        )
                    ]
                }
            )
