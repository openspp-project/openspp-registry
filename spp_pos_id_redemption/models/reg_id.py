# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.


from odoo import models


class G2PRegistrantID(models.Model):
    _inherit = "g2p.reg.id"

    def generate_id_card(self):
        for rec in self:
            id_card = self.env.ref("spp_pos_id_redemption.action_report_id_barcode_printout").report_action(rec)
            return id_card
