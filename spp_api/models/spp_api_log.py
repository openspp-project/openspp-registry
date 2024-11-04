# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class Log(models.Model):
    _name = "spp_api.log"
    _order = "id desc"
    _description = "OpenAPI logs"

    name = fields.Char(compute="_compute_name")
    method = fields.Selection(
        [
            ("get", "Read"),
            ("post", "Create"),
            ("put", "Update"),
            ("delete", "Delete"),
            ("patch", "Custom function"),
        ],
        required=True,
    )
    http_type = fields.Selection(
        [
            ("request", "Request"),
            ("response", "Response"),
        ],
        required=True,
    )
    model = fields.Char(required=True)
    namespace_id = fields.Many2one("spp_api.namespace", "Integration")
    request = fields.Text()

    request_id = fields.Text(string="Request ID")
    request_parameter = fields.Text()
    request_data = fields.Text()

    reply_id = fields.Text()
    response_data = fields.Text()

    def _compute_name(self):
        self.name = f"{self.http_type} {self.method} - {self.model}"
