# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import hashlib
import logging
import math
import random

from dateutil.relativedelta import relativedelta
from faker import Faker

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class G2PGenerateData(models.Model):
    _name = "spp.generate.data"
    _description = "Generate Sample Data"

    name = fields.Char()
    num_groups = fields.Integer("Number of Groups", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    def generate_sample_data(self):
        # celery = {
        #    "countdown": 3,
        #    "retry": True,
        #    "retry_policy": {"max_retries": 2, "interval_start": 2},
        # }
        batches = math.ceil(self.num_groups / 1000)
        for _i in range(0, batches):
            # self.env["celery.task"].call_task(
            #    self._name, "_generate_sample_data", res_id=self.id, celery=celery
            # )
            self.with_delay()._generate_sample_data(res_id=self.id)

    @api.model
    def _generate_sample_data(self, **kwargs):
        """
        Generate sample data for testing
        Returns:

        """
        res_id = kwargs.get("res_id")
        res = self.browse(res_id)
        locales = [
            "cs_CZ",
            "en_US",
            "de_CH",
            "ar_AA",
            "de_DE",
            "en_GB",
            "en_IE",
            "en_TH",
            "es_ES",
            "es_MX",
            "fr_FR",
            "hi_IN",
            "hr_HR",
            "it_IT",
            "zh_CN",
        ]
        fake = Faker(locales)

        # Get available gender field selections
        options = self.env["gender.type"].search([])
        sex_choices = [option.value for option in options]
        sex_choice_range = sex_choices * 50

        age_group_range = ["A", "C"] * 2 + ["E"]
        group_size_range = list(range(1, 2)) * 2 + list(range(3, 5)) * 4 + list(range(6, 8))

        group_membership_kind_head_id = self.env.ref("g2p_registry_membership.group_membership_kind_head").id
        group_kind_household_id = self.env.ref("g2p_registry_group.group_kind_household").id
        group_kind_family_id = self.env.ref("g2p_registry_group.group_kind_family").id

        num_groups = min(res.num_groups, 1000)
        for i in range(0, num_groups):
            locale = random.choice(locales)
            group_size = random.choice(group_size_range)
            last_name = fake[locale].last_name()

            registration_date = (
                fake[locale]
                .date_between_dates(
                    date_start=datetime.datetime.now() - relativedelta(weeks=4),
                    date_end=datetime.datetime.now(),
                )
                .isoformat()
            )

            head = res._generate_individual_data(
                fake[locale],
                last_name,
                sex_choice_range,
                age_group_range,
                registration_date,
            )

            head["is_head"] = True

            group_id = "demo." + hashlib.md5(f"{last_name} {i}".encode()).hexdigest()

            group_kind = random.choice([group_kind_household_id, group_kind_family_id])

            group = {
                "id": group_id,
                "name": last_name,
                "is_group": True,
                "is_registrant": True,
                "registration_date": registration_date,
                "kind": group_kind,
            }

            create_group_id = self.env["res.partner"].create(group)

            head["id"] = f"{group_id}-0"
            members = [head]

            for i in range(group_size - 1):
                data = res._generate_individual_data(
                    fake[locale],
                    last_name,
                    sex_choice_range,
                    age_group_range,
                    registration_date,
                )

                data["id"] = f"{group_id}-{i+1}"
                members.append(data)

            # add this on membership
            if random.randint(0, 2) == 0:
                members[0]["is_principal_recipient"] = True
            else:
                members[random.randint(0, group_size - 1)]["is_principal_recipient"] = True

            for member in members:
                is_head = True if (member and member.get("is_head")) else False
                is_principal_recipient = True if (member and member.get("is_principal_recipient")) else False

                if is_head:
                    member.pop("is_head", None)
                    member.pop("is_principal_recipient", None)
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                            "kind": [
                                (
                                    4,
                                    group_membership_kind_head_id,
                                )
                            ],
                        }
                    )

                elif is_principal_recipient:
                    member.pop("is_head", None)
                    member.pop("is_principal_recipient", None)
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                            "kind": [],
                        }
                    )

                else:
                    create_member_id = self.env["res.partner"].create(member)
                    self.env["g2p.group.membership"].create(
                        {
                            "group": create_group_id.id,
                            "individual": create_member_id.id,
                        }
                    )

            if res.state == "draft":
                res.update({"state": "generate"})

        msg = "Task Queue called task: model [{}] and method [{}].".format(
            self._name,
            "_generate_sample_data",
        )
        _logger.info(msg)
        return {"result": msg, "res_model": self._name, "res_ids": [res_id]}
        # _logger.info("-" * 80)
        # _logger.info(json.dumps({"group": group, "members": members}, indent=4))

    def _generate_individual_data(self, fake, last_name, sex_choice_range, age_group_range, registration_date):
        sex = random.choice(sex_choice_range)
        age_group = random.choice(age_group_range)
        first_name = fake.first_name_male() if sex == "Male" else fake.first_name_female()
        different_last_name = random.randint(0, 100) < 10
        if age_group == "C":
            date_start = datetime.datetime.now() - relativedelta(years=17)
            date_end = datetime.datetime.now()
        elif age_group == "A":
            date_start = datetime.datetime.now() - relativedelta(years=65)
            date_end = datetime.datetime.now() - relativedelta(years=18)
        else:
            date_start = datetime.datetime.now() - relativedelta(years=100)
            date_end = datetime.datetime.now() - relativedelta(years=65)

        if different_last_name:
            last_name = fake.last_name()

        medical_condition = 0
        if random.randint(0, 100) < 5:
            medical_condition = random.randint(10, 100)

        disability_level = 0
        if random.randint(0, 100) < 2:
            disability_level = random.randint(10, 100)

        pregnancy_start = None
        lactation_start = None
        if sex == "Female" and age_group == "A":
            rnd = random.randint(0, 100)
            if rnd < 15:
                pregnancy_start = fake.date_between_dates(
                    date_start=datetime.datetime.now() - relativedelta(months=9),
                    date_end=datetime.datetime.now(),
                ).isoformat()
            elif rnd > 80:
                lactation_start = fake.date_between_dates(
                    date_start=datetime.datetime.now() - relativedelta(months=24),
                    date_end=datetime.datetime.now(),
                ).isoformat()

        dob = fake.date_between_dates(date_start=date_start, date_end=date_end).isoformat()

        fullname = f"{first_name} {last_name}"

        return {
            "name": fullname,
            "given_name": first_name,
            "family_name": last_name,
            "gender": sex,
            "birthdate": dob,
            "is_registrant": True,
            "is_group": False,
            "registration_date": registration_date,
            "z_cst_indv_disability_level": disability_level,
            "z_cst_indv_medical_condition": medical_condition,
            "z_cst_indv_pregnancy_start": pregnancy_start,
            "z_cst_indv_lactation_start": lactation_start,
        }
