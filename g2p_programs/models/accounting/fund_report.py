# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ProgramFundReport(models.Model):
    _name = "g2p.program.fund.report.view"
    _description = "Program Fund Report"
    _auto = False
    _table = "g2p_program_fund_report_view"

    name = fields.Char("Source Document", readonly=True)
    partner_id = fields.Many2one("res.partner", "Beneficiary", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    program_id = fields.Many2one("g2p.program", "Program", readonly=True)
    cycle_id = fields.Many2one("g2p.cycle", "Cycle", readonly=True)
    journal_id = fields.Many2one("account.journal", "Accounting Journal", readonly=True)
    date_posted = fields.Date("Date", readonly=True)
    amount = fields.Monetary(required=True, currency_field="currency_id", readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)

    def _select(self):
        select_str = """
            WITH trans AS (
                SELECT a1.name as name,
                    NULL as partner_id,
                    a1.company_id as company_id,
                    a1.program_id as program_id,
                    NULL as cycle_id,
                    a1.journal_id as journal_id,
                    a1.date_posted as date_posted,
                    a1.amount as amount,
                    a1.currency_id as currency_id
                FROM g2p_program_fund a1
                WHERE a1.state = 'posted'

                UNION ALL

                SELECT b1.code as name,
                    b1.partner_id as partner_id,
                    b1.company_id as company_id,
                    b3.id as program_id,
                    b2.id as cycle_id,
                    b1.journal_id as journal_id,
                    b5.date as date_posted,
                    b4.amount * -1 as amount,
                    b4.currency_id as currency_id
                FROM g2p_entitlement b1
                    LEFT JOIN g2p_cycle b2 on b2.id = b1.cycle_id
                        LEFT JOIN g2p_program b3 on b3.id = b2.program_id
                    LEFT JOIN account_payment b4 on b4.id = b1.disbursement_id
                        LEFT JOIN account_move b5 on b5.id = b4.move_id
                WHERE b1.disbursement_id IS NOT NULL and b4.payment_type = 'outbound'
            )

            SELECT
                ROW_NUMBER () OVER (
                    ORDER BY date_posted) as id,
                name,
                partner_id,
                company_id,
                program_id,
                cycle_id,
                journal_id,
                date_posted,
                amount,
                currency_id
            FROM trans
            ORDER BY date_posted
        """
        return select_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""CREATE or REPLACE VIEW {self._table} as (
            {self._select()}
            )"""
        )
