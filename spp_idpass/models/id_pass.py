# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json
import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OpenSPPIDPass(models.Model):
    _name = "spp.id.pass"
    _description = "ID Pass"

    name = fields.Char("Template Name")
    api_url = fields.Text("API URL")
    api_username = fields.Char("API Username")
    api_password = fields.Char("API Password")
    filename_prefix = fields.Char("File Name Prefix")
    expiry_length = fields.Integer("ID Expiry Length", default=1)
    expiry_length_type = fields.Selection(
        [("years", "Years"), ("months", "Months"), ("days", "Days")],
        "Length Type",
        default="years",
    )
    auth_token_url = fields.Text()
    auth_token = fields.Text()
    is_active = fields.Boolean("Active")
    id_type = fields.Many2one("g2p.id.type")

    def generate_auth_token(self):
        """
        This generates the auth token from auth_token_url, api_username
        and api_password
        """
        for rec in self:
            if rec.auth_token_url and rec.api_username and rec.api_password:
                data = {"username": rec.api_username, "password": rec.api_password}
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }

                response = requests.post(
                    rec.auth_token_url,
                    data=json.dumps(data),
                    headers=headers,
                    timeout=10,
                )
                if response.status_code == 200:
                    response_json = response.json()
                    rec.auth_token = response_json["token"]
        return
