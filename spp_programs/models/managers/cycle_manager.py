from odoo import models


class CustomDefaultCycleManager(models.Model):
    _inherit = "g2p.cycle.manager.default"

    def on_start_date_change(self, cycle):
        pass

    def mark_prepare_entitlement_as_done(self, cycle, msg):
        """Complete the preparation of entitlements.
        Base :meth:`mark_prepare_entitlement_as_done`.
        This is executed when all the jobs are completed.
        Post a message in the chatter.

        :param cycle: A recordset of cycle
        :param msg: A string to be posted in the chatter
        :return:
        """
        super().mark_prepare_entitlement_as_done(cycle, msg)
        # Update Statistics
        cycle._compute_inkind_entitlements_count()
        return

    def _prepare_entitlements(self, cycle, offset=0, limit=None, do_count=False):
        """Prepare Entitlements
        Get the beneficiaries and generate their entitlements.

        :param cycle: The cycle
        :param offset: Optional integer value for the ORM search offset
        :param limit: Optional integer value for the ORM search limit
        :param do_count: Boolean - set to False to not run compute function
        :return:
        """
        super()._prepare_entitlements(cycle, offset, limit, do_count)
        if do_count:
            # Update Statistics
            cycle._compute_inkind_entitlements_count()
        return

    def new_cycle(self, name, new_start_date, sequence):
        for rec in self:
            latest_cycle = rec.program_id.cycle_ids.sorted(key="create_date", reverse=True)[:1]
            cycle = super(CustomDefaultCycleManager, rec).new_cycle(name, new_start_date, sequence)
            latest_cycle.write({"next_cycle_id": cycle.id})
            cycle.write({"prev_cycle_id": latest_cycle.id})
            return cycle
