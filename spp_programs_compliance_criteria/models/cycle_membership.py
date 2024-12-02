from odoo import fields, models


class G2PCycleMembership(models.Model):
    _inherit = "g2p.cycle.membership"

    state = fields.Selection(
        selection_add=[
            ("non_compliant", "Non-Compliant"),
        ],
        default="draft",
        copy=False,
    )
