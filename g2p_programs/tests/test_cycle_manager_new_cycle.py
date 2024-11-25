from datetime import datetime

from freezegun import freeze_time

from odoo.tests.common import TransactionCase

from odoo.addons.g2p_programs.models.constants import MANAGER_PROGRAM


@freeze_time("2022-12-15")
class DefaultCycleManagerTest(TransactionCase):
    DATE_TODAY = datetime(2022, 12, 15).date()

    def create_program_manager(self, **kwargs):
        data = kwargs
        data.update(
            {
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
            }
        )
        program_wizard = self.env["g2p.program.create.wizard"].create(data)
        result = program_wizard.create_program()

        program = self.env[result["res_model"]].browse(result["res_id"])
        return program.get_manager(MANAGER_PROGRAM)

    def test_new_cycle_daily(self):
        # create and test a 20 day cycle
        program_manager_data = {
            "name": "Daily",
            "rrule_type": "daily",
            "cycle_duration": 20,
        }

        program_manager = self.create_program_manager(**program_manager_data)
        first_cycle = program_manager.new_cycle()

        self.assertEqual(first_cycle.start_date, self.DATE_TODAY)
        self.assertEqual(first_cycle.end_date, datetime(2023, 1, 3).date())
        self.assertEqual(first_cycle.sequence, 1)

        second_cycle = program_manager.new_cycle()

        self.assertEqual(second_cycle.start_date, datetime(2023, 1, 4).date())
        self.assertEqual(second_cycle.end_date, datetime(2023, 1, 23).date())
        self.assertEqual(second_cycle.sequence, 2)

    def test_new_cycle_yearly(self):
        # create and test a yearly cycle with 1 cycle duration

        program_manager_data = {
            "name": "Yearly",
            "rrule_type": "yearly",
            "cycle_duration": 1,
        }

        program_manager = self.create_program_manager(**program_manager_data)

        first_cycle = program_manager.new_cycle()

        self.assertEqual(first_cycle.start_date, self.DATE_TODAY)
        self.assertEqual(first_cycle.end_date, datetime(2023, 12, 14).date())
        self.assertEqual(first_cycle.sequence, 1)

        second_cycle = program_manager.new_cycle()

        self.assertEqual(second_cycle.start_date, datetime(2023, 12, 15).date())
        self.assertEqual(second_cycle.end_date, datetime(2024, 12, 14).date())
        self.assertEqual(second_cycle.sequence, 2)

    def test_new_cycle_monthly_month_by_date(self):
        # create and test a monthly cycle with 1 cycle duration every 10th day of the month

        program_manager_data = {
            "name": "Monthly every 10th",
            "rrule_type": "monthly",
            "cycle_duration": 1,
            "month_by": "date",
            "day": 10,
        }

        program_manager = self.create_program_manager(**program_manager_data)

        first_cycle = program_manager.new_cycle()

        self.assertEqual(first_cycle.start_date, datetime(2023, 1, 10).date())
        self.assertEqual(first_cycle.end_date, datetime(2023, 2, 9).date())
        self.assertEqual(first_cycle.sequence, 1)

        second_cycle = program_manager.new_cycle()

        self.assertEqual(second_cycle.start_date, datetime(2023, 2, 10).date())
        self.assertEqual(second_cycle.end_date, datetime(2023, 3, 9).date())
        self.assertEqual(second_cycle.sequence, 2)

    def test_new_cycle_monthly_month_by_day(self):
        # create and test a monthly cycle with 1 cycle duration every first monday of the month

        program_manager_data = {
            "name": "Monthly every first monday of the month",
            "rrule_type": "monthly",
            "cycle_duration": 1,
            "month_by": "day",
            "byday": "1",
            "weekday": "MON",
        }

        program_manager = self.create_program_manager(**program_manager_data)

        first_cycle = program_manager.new_cycle()

        self.assertEqual(first_cycle.start_date, datetime(2023, 1, 2).date())
        self.assertEqual(first_cycle.end_date, datetime(2023, 2, 5).date())
        self.assertEqual(first_cycle.sequence, 1)

        second_cycle = program_manager.new_cycle()

        self.assertEqual(second_cycle.start_date, datetime(2023, 2, 6).date())
        self.assertEqual(second_cycle.end_date, datetime(2023, 3, 5).date())
        self.assertEqual(second_cycle.sequence, 2)

    def test_new_cycle_weekly(self):
        # create and test a weekly cycle with 1 cycle duration every monday

        program_manager_data = {
            "name": "Weekly every monday",
            "rrule_type": "weekly",
            "cycle_duration": 1,
            "mon": True,
        }

        program_manager = self.create_program_manager(**program_manager_data)

        first_cycle = program_manager.new_cycle()

        self.assertEqual(first_cycle.start_date, datetime(2022, 12, 19).date())
        self.assertEqual(first_cycle.end_date, datetime(2022, 12, 25).date())
        self.assertEqual(first_cycle.sequence, 1)

        second_cycle = program_manager.new_cycle()

        self.assertEqual(second_cycle.start_date, datetime(2022, 12, 26).date())
        self.assertEqual(second_cycle.end_date, datetime(2023, 1, 1).date())
        self.assertEqual(second_cycle.sequence, 2)
