# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    inkind_entitlement_ids = fields.One2many("g2p.entitlement.inkind", "cycle_id", "In-Kind Entitlements")
    inkind_entitlements_count = fields.Integer(string="# In-kind Entitlements", readonly=True)

    # Stock Management Fields
    picking_ids = fields.One2many("stock.picking", "cycle_id", string="Stock Transfers")
    procurement_group_id = fields.Many2one("procurement.group", "Procurement Group")

    validate_async_err = fields.Boolean(default=False)

    prev_cycle_id = fields.Many2one("g2p.cycle", "Previous Cycle", readonly=True)
    next_cycle_id = fields.Many2one("g2p.cycle", "Next Cycle", readonly=True)

    def _compute_inkind_entitlements_count(self):
        for rec in self:
            entitlements_count = self.env["g2p.entitlement.inkind"].search_count([("cycle_id", "=", rec.id)])
            rec.update({"inkind_entitlements_count": entitlements_count})

    def get_previous_cycle(self):
        self.ensure_one()
        if self.prev_cycle_id:
            return self.prev_cycle_id
        else:
            sorted_cycles = self.program_id.cycle_ids.sorted(key="create_date")
            current_index = sorted_cycles.ids.index(self.id)
            if current_index > 0:
                # Return the previous cycle
                self.prev_cycle_id = sorted_cycles[current_index - 1]
                return sorted_cycles[current_index - 1]
            else:
                # Return None or False if there is no previous cycle
                return None

    def get_next_cycle(self):
        self.ensure_one()
        if self.next_cycle_id:
            return self.next_cycle_id
        else:
            sorted_cycles = self.program_id.cycle_ids.sorted(key="create_date")
            current_index = sorted_cycles.ids.index(self.id)
            if current_index < len(sorted_cycles) - 1:
                # Return the next cycle
                self.next_cycle_id = sorted_cycles[current_index + 1]
                return sorted_cycles[current_index + 1]
            else:
                # Return None or False if there is no next cycle
                return None

    def get_entitlements(
        self,
        state,
        entitlement_model="g2p.entitlement",
        offset=0,
        limit=None,
        order=None,
        count=False,
    ):
        """
        Query entitlements based on state.
        Overrides OpenG2P's get_entitlements method to fix the issue with search_count offset parameter.
        :param state: List of states
        :param entitlement_model: String value of entitlement model to search
        :param offset: Optional integer value for the ORM search offset
        :param limit: Optional integer value for the ORM search limit
        :param order: Optional string value for the ORM search order fields
        :param count: Optional boolean for executing a search-count (if true) or search (if false: default)
        :return:
        """
        domain = [("cycle_id", "=", self.id)]
        if state:
            if isinstance(state, str):
                state = [state]
            domain += [("state", "in", state)]

        if count:
            return self.env["g2p.cycle.membership"].search_count(domain, limit=limit)
        return self.env[entitlement_model].search(domain, offset=offset, limit=limit, order=order)

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.start_date < fields.Date.today():
                raise ValidationError(_('The "Start Date" cannot be earlier than today.'))
            if record.end_date and record.start_date and record.end_date < record.start_date:
                raise ValidationError(_('The "End Date" cannot be earlier than the "Start Date".'))
