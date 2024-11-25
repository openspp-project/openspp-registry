# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # Custom Fields
    beneficiary_disb = fields.Boolean("Beneficiary Funds")
