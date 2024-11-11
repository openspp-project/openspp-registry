import hashlib
import json
import math
import random
import string
from datetime import datetime, timedelta

from odoo import Command, api, fields, models

from odoo.addons.spp_base_demo.locale_providers import create_faker

from .. import tools

LOCALES = {
    "en_KE": {
        "name": "Kenya (English)",
        "location_function": tools.random_location_in_kenya,
    },
    "sw_KE": {
        "name": "Kenya (Swahili)",
        "location_function": tools.random_location_in_kenya,
    },
    "lo_LA": {
        "name": "Laos (Lao)",
        "location_function": tools.random_location_in_laos,
    },
    "si_LK": {
        "name": "Sri Lanka (Sinhala)",
        "location_function": tools.random_location_in_sri_lanka,
    },
    "ta_LK": {
        "name": "Sri Lanka (Tamil)",
        "location_function": tools.random_location_in_sri_lanka,
    },
}


class SPPGenerateFarmerData(models.Model):
    _name = "spp.generate.farmer.data"
    _description = "Generate Farm Data"

    LOCALE_SELECTION = [(key, value["name"]) for key, value in LOCALES.items()]

    name = fields.Char()
    num_groups = fields.Integer("Number of Groups", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    locale = fields.Selection(
        LOCALE_SELECTION,
        default="en_KE",
        required=True,
    )

    def generate_sample_data(self):
        batches = math.ceil(self.num_groups / 1000)

        for _ in range(0, batches):
            # self.with_delay()._generate_sample_data(res_id=self.id)
            self._generate_sample_data(res=self)

    @api.model
    def _generate_sample_data(self, **kwargs):
        res = kwargs.get("res")

        kind_farm_id = self.env.ref("spp_farmer_registry_base.kind_farm").id

        fake = create_faker(res.locale)

        # Get available gender field selections
        options = self.env["gender.type"].search([])
        sex_choices = [option.value for option in options]
        sex_choice_range = sex_choices * 50

        num_groups = min(res.num_groups, 1000)

        for i in range(0, num_groups):
            group_id = res._generate_group_data(i, fake, sex_choice_range, kind_farm_id)

            land_record_id = res._generate_land_record_record(group_id, res.locale)
            group_id.farm_land_rec_id = land_record_id.id
            group_id.coordinates = land_record_id.land_coordinates

            # create a random number of agricultural activities
            for _ in range(random.randint(1, 5)):
                crop_farm_species_id = res._get_species_data(species_type="crop")
                live_farm_species_id = res._get_species_data()
                aqua_farm_species_id = res._get_species_data(species_type="aquaculture")

                res._generate_agricultural_activity_data(
                    activity_type="crop",
                    crop_farm_id=group_id.id,
                    land_id=land_record_id.id,
                    species_id=crop_farm_species_id.id,
                )

                res._generate_agricultural_activity_data(
                    activity_type="livestock",
                    live_farm_id=group_id.id,
                    land_id=land_record_id.id,
                    species_id=live_farm_species_id.id,
                )

                res._generate_agricultural_activity_data(
                    activity_type="aquaculture",
                    aqua_farm_id=group_id.id,
                    land_id=land_record_id.id,
                    species_id=aqua_farm_species_id.id,
                )

            farm_details_data = res._generate_farm_details_data()
            group_id.farm_detail_id.write(farm_details_data)

            for _ in range(random.randint(3, 7)):
                asset_type_id = res._get_asset_type_data()
                machinery_type_id = res._get_machinery_type_data()

                res._generate_farm_asset_data(
                    asset_farm_id=group_id.id,
                    land_id=land_record_id.id,
                    asset_type_id=asset_type_id,
                )

                res._generate_farm_asset_data(
                    machinery_farm_id=group_id.id,
                    land_id=land_record_id.id,
                    machinery_type_id=machinery_type_id,
                )

            if res.state == "draft":
                res.update({"state": "generate"})

        msg = "Task Queue called task: model [{}] and method [{}].".format(
            self._name,
            "_generate_sample_data",
        )

        return {"result": msg, "res_model": self._name, "res_ids": [res.id]}

    def _generate_group_data(self, index, fake, sex_choice_range, kind_id):
        sex = random.choice(sex_choice_range)
        last_name = fake.last_name()
        first_name = fake.first_name_male() if sex == "Male" else fake.first_name_female()
        addl_name = fake.first_name_male() if sex == "Male" else fake.first_name_female()

        group_name = f"{last_name} Farm"
        id_group = "demo." + hashlib.md5(f"{group_name} {index}".encode()).hexdigest()

        highest_education_level = [
            "none",
            "primary",
            "secondary",
            "tertiary",
        ]

        marital_status = [
            "single",
            "married",
            "married_monogamous",
            "married_polygamous",
            "widowed",
            "separated",
        ]

        farmer_mobile_tel = "+2547" + "".join(random.choices("0123456789", k=8))

        start_date = datetime(year=1950, month=1, day=1)
        end_date = datetime(year=2003, month=12, day=31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        farmer_birthdate = start_date + timedelta(days=random_number_of_days)
        farmer_email = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5)) + "@example.com"
        farmer_household_size = str(random.randint(1, 10))
        farmer_postal_address = "P.O Box " + "".join(random.choices("0123456789", k=4))

        group_vals = {
            "id": id_group,
            "name": group_name,
            "kind": kind_id,
            "is_registrant": True,
            "is_group": True,
            "farmer_family_name": last_name,
            "farmer_given_name": first_name,
            "farmer_national_id": "".join(random.choices(string.ascii_uppercase + string.digits, k=10)),
            "farmer_sex": sex,
            "farmer_addtnl_name": addl_name,
            "farmer_marital_status": random.choice(marital_status),
            "farmer_highest_education_level": random.choice(highest_education_level),
            "farmer_mobile_tel": farmer_mobile_tel,
            "farmer_birthdate": farmer_birthdate,
            "farmer_email": farmer_email,
            "farmer_formal_agricultural": random.choice([True, False]),
            "farmer_household_size": farmer_household_size,
            "farmer_postal_address": farmer_postal_address,
        }
        return self.env["res.partner"].create(group_vals)

    def _generate_land_record_record(self, group_id, locale):
        random_location_function = LOCALES[locale]["location_function"]

        latitude, longitude = random_location_function()

        land_coordinates = {"type": "Point", "coordinates": [longitude, latitude]}

        points = tools.generate_polygon(latitude, longitude, random.randrange(50, 500))

        land_geo_polygon = {"type": "Polygon", "coordinates": [points]}

        return self.env["spp.land.record"].create(
            {
                "land_farm_id": group_id.id,
                "land_name": group_id.name,
                "land_coordinates": json.dumps(land_coordinates),
                "land_geo_polygon": json.dumps(land_geo_polygon),
            }
        )

    def _generate_agricultural_activity_data(
        self,
        activity_type="crop",
        crop_farm_id=None,
        live_farm_id=None,
        aqua_farm_id=None,
        land_id=None,
        species_id=None,
    ):
        # Define the possible values for selection fields
        purposes = ["subsistence", "commercial", "both"]
        cultivation_water_sources = ["irrigated", "rainfed"]
        cultivation_production_systems = [
            "Mono-cropping",
            "Mixed-cropping",
            "Agroforestry",
            "Plantation",
            "Greenhouse",
        ]
        cultivation_chemical_interventions = self.env["spp.farm.chemical"].search([]).mapped("id")
        cultivation_fertilizer_interventions = self.env["spp.fertilizer"].search([]).mapped("id")
        livestock_production_systems = [
            "ranching",
            "communal grazing",
            "pastoralism",
            "rotational grazing",
            "zero grazing",
            "semi zero grazing",
            "feedlots",
            "free range",
            "tethering",
            "other",
        ]
        livestock_feed_items = self.env["spp.feed.items"].search([]).mapped("id")
        aquaculture_production_systems = [
            "ponds",
            "cages",
            "tanks",
            "raceways",
            "recirculating systems",
            "aquaponics",
            "other",
        ]

        # Produce random quantity of chemical/fertilizer/feed items to be created
        chemical_interventions_len = random.randint(1, len(cultivation_chemical_interventions))
        fertilizer_interventions_len = random.randint(1, len(cultivation_fertilizer_interventions))
        feed_items_len = random.randint(1, len(livestock_feed_items))

        # Generate the chemical/fertilizer/feed items based on the quantity
        chemical_interventions_vals = []
        for _ in range(chemical_interventions_len):
            chemical_interventions_vals.append(Command.link(random.choice(cultivation_chemical_interventions)))
        chemical_interventions_vals = list(dict.fromkeys(chemical_interventions_vals))
        fertilizer_interventions_vals = []

        for _ in range(fertilizer_interventions_len):
            fertilizer_interventions_vals.append(Command.link(random.choice(cultivation_fertilizer_interventions)))
        fertilizer_interventions_vals = list(dict.fromkeys(fertilizer_interventions_vals))

        feed_items_interventions_vals = []
        for _ in range(feed_items_len):
            feed_items_interventions_vals.append(Command.link(random.choice(livestock_feed_items)))
        feed_items_interventions_vals = list(dict.fromkeys(feed_items_interventions_vals))

        # Generate a random value for each field
        data = {
            "crop_farm_id": crop_farm_id,
            "live_farm_id": live_farm_id,
            "aqua_farm_id": aqua_farm_id,
            "land_id": land_id,
            "species_id": species_id,
            "purpose": random.choice(purposes),
            "activity_type": activity_type,
            "cultivation_water_source": random.choice(cultivation_water_sources),
            "cultivation_production_system": random.choice(cultivation_production_systems),
            "cultivation_chemical_interventions": chemical_interventions_vals,
            "cultivation_fertilizer_interventions": fertilizer_interventions_vals,
            "livestock_production_system": random.choice(livestock_production_systems),
            "livestock_feed_items": feed_items_interventions_vals,
            "aquaculture_production_system": random.choice(aquaculture_production_systems),
            "aquaculture_number_of_fingerlings": random.randint(
                0, 1000
            ),  # Assuming a reasonable range for number of fingerlings
        }

        # Clean up data based on activity_type
        if data["activity_type"] != "crop":
            data.pop("cultivation_water_source")
            data.pop("cultivation_production_system")
            data.pop("cultivation_chemical_interventions")
            data.pop("cultivation_fertilizer_interventions")

        if data["activity_type"] != "livestock":
            data.pop("livestock_production_system")
            data.pop("livestock_feed_items")

        if data["activity_type"] != "aquaculture":
            data.pop("aquaculture_production_system")
            data.pop("aquaculture_number_of_fingerlings")

        return self.env["spp.farm.activity"].create(data)

    def _generate_farm_asset_data(
        self,
        asset_farm_id=None,
        machinery_farm_id=None,
        land_id=None,
        asset_type_id=None,
        machinery_type_id=None,
    ):
        # Generate random data for the fields not requiring a reference to another object
        quantity = random.randint(1, 100)
        machine_working_status = random.choice(["Working", "Needs maintenance", "Broken"])
        number_active = random.randint(0, quantity)
        active_area = round(random.uniform(1.0, 100.0), 2)
        active_volume = round(random.uniform(1.0, 100.0), 2)
        number_inactive = quantity - number_active
        inactive_area = round(random.uniform(1.0, 100.0), 2)
        inactive_volume = round(random.uniform(1.0, 100.0), 2)

        # Construct the data dictionary
        farm_asset_data = {
            "asset_farm_id": asset_farm_id,
            "machinery_farm_id": machinery_farm_id,
            "land_id": land_id,
            "asset_type": asset_type_id,
            "machinery_type": machinery_type_id,
            "quantity": quantity,
            "machine_working_status": machine_working_status,
            "number_active": number_active,
            "active_area": active_area,
            "active_volume": active_volume,
            "number_inactive": number_inactive,
            "inactive_area": inactive_area,
            "inactive_volume": inactive_volume,
        }

        # "spp.farm.asset"
        return self.env["spp.farm.asset"].create(farm_asset_data)

    def _generate_farm_details_data(
        self,
    ):
        # Generate random data for the fields not requiring a reference to another object
        farm_types = ["crop", "livestock", "aquaculture", "mixed"]
        legal_statuses = [
            "self",
            "family",
            "extended community",
            "cooperative",
            "government",
            "leased",
            "unknown",
        ]
        water_body_types = ["freshwater", "marine", "brackish"]
        power_sources = [
            "manual labor",
            "animal drought",
            "motorized",
            "wind",
            "solar",
            "grid electricity",
            "other",
        ]
        labor_sources = [
            "family members",
            "temporary hired help",
            "permanent hired help",
        ]
        equipment_owners = ["self", "community", "hirer"]
        irrigation_types = [
            "furrow_canal",
            "basin",
            "bucket",
            "centre_pivot",
            "drip",
            "furrow",
            "sprinkler",
            "flooding",
            "other",
        ]
        irrigation_sources = [
            "locality water supply",
            "water trucking",
            "rain",
            "natural rivers and streams",
            "man made dam",
            "shallow well or borehole",
            "adjacent water body",
            "harvested water",
            "road runoff",
            "water pan",
        ]
        irrigation_projects = [
            "public irrigation scheme",
            "private on farm initiative",
            "community scheme",
        ]
        management_implementing_bodies = [
            "county government",
            "national government",
            "implementing agents",
            "national govt ministry",
            "self",
            "other",
        ]
        scheme_memberships = ["full member", "out grower"]
        income_sources = [
            "sale of farming produce",
            "non-farm trading",
            "salary from employment elsewhere",
            "casual labor elsewhere",
            "pension",
            "remittances",
            "cash transfer",
            "other",
        ]
        extension_services = [
            "e-extension",
            "face-to-face",
            "farmer field schools",
            "group demonstrations",
            "peer-to-peer",
            "other",
        ]

        implementing_bodies = [
            "county government",
            "national government",
            "private",
            "ngo",
            "other",
        ]

        main_source_informations = [
            "newspaper",
            "extension services",
            "internet",
            "radio",
            "television",
            "public gatherings",
            "relatives",
        ]

        # Randomly select true or false for boolean fields
        def random_bool():
            return random.choice([True, False])

        farm_details_data = {
            "details_farm_type": random.choice(farm_types),
            "farm_total_size": round(random.uniform(0.1, 1000.0), 2),
            "farm_size_under_crops": round(random.uniform(0.1, 1000.0), 2),
            "farm_size_under_livestock": round(random.uniform(0.1, 1000.0), 2),
            "farm_size_leased_out": round(random.uniform(0.1, 1000.0), 2),
            "farm_size_idle": round(random.uniform(0.1, 1000.0), 2),
            "details_legal_status": random.choice(legal_statuses),
            "lease_term": random.randint(1, 99),
            "lease_agreement_number": "".join(random.choices(string.ascii_uppercase + string.digits, k=10)),
            "another_farm": random_bool(),
            "growing_crops_subsistence": random_bool(),
            "growing_crops_sale": random_bool(),
            "rearing_livestock_subsistence": random_bool(),
            "rearing_livestock_sale": random_bool(),
            "tree_farming": random_bool(),
            "livestock_fertilizer_for_fodder": random_bool(),
            "livestock_certified_pasture": random_bool(),
            "livestock_assisted_reproductive_health_technology_ai": random_bool(),
            "livestock_assisted_reproductive_health_technology_animal_horm": random_bool(),
            "livestock_assisted_reproductive_health_technology_embryo_transf": random_bool(),
            "livestock_animal_health_services_routine_vaccination": random_bool(),
            "livestock_animal_health_services_disease_control": random_bool(),
            "aquaculture_type": random.choice(water_body_types),
            "aquaculture_subsistence": random_bool(),
            "aquaculture_sale": random_bool(),
            "aquaculture_main_inputs_fingerlings": random_bool(),
            "aquaculture_main_inputs_feeds": random_bool(),
            "aquaculture_main_inputs_fertilizers": random_bool(),
            "aquaculture_utilize_fertilizer": random_bool(),
            "aquaculture_production_level": random.choice(["extensive", "semi-intensive", "intensive"]),
            "aquaculture_beneficiary_esp": random_bool(),
            "farm_technology_power_source": random.choice(power_sources),
            "farm_technology_labor_source": random.choice(labor_sources),
            "farm_technology_own_equipment": random.choice(equipment_owners),
            "farm_technology_structure_spray_race": random_bool(),
            "financial_services_main_income_source": random.choice(income_sources),
            "farm_technology_structure_animal_dip": random_bool(),
            "farm_technology_structure_zero_grazing_unit": random_bool(),
            "farm_technology_structure_hay_store": random_bool(),
            "farm_technology_structure_feed_store": random_bool(),
            "farm_technology_structure_sick_bay": random_bool(),
            "farm_technology_structure_cattle_boma": random_bool(),
            "farm_technology_structure_milking_parlor": random_bool(),
            "farm_technology_structure_animal_crush": random_bool(),
            "farm_technology_structure_traditional_granary": random_bool(),
            "farm_technology_structure_modern_granary": random_bool(),
            "farm_technology_structure_general_store": random_bool(),
            "farm_technology_structure_hay_bailers": random_bool(),
            "farm_technology_structure_green_house": random_bool(),
            "farm_technology_structure_bee_house": random_bool(),
            "farm_technology_structure_hatchery": random_bool(),
            "farm_technology_structure_apriary": random_bool(),
            "land_water_management_crop_rotation": random_bool(),
            "land_water_management_green_cover_crop": random_bool(),
            "land_water_management_contour_ploughing": random_bool(),
            "land_water_management_deep_ripping": random_bool(),
            "land_water_management_grass_strips": random_bool(),
            "land_water_management_trash_line": random_bool(),
            "land_water_management_cambered_beds": random_bool(),
            "land_water_management_biogas_production": random_bool(),
            "land_water_management_mulching": random_bool(),
            "land_water_management_minimum_tillage": random_bool(),
            "land_water_management_manuring_composting": random_bool(),
            "land_water_management_organic_farming": random_bool(),
            "land_water_management_terracing": random_bool(),
            "land_water_management_water_harvesting": random_bool(),
            "land_water_management_zai_pits": random_bool(),
            "land_water_management_cut_off_drains": random_bool(),
            "land_water_management_conservation_agriculture": random_bool(),
            "land_water_management_integrated_pest_management": random_bool(),
            "land_water_management_subsidized_fertilizer": random_bool(),
            "land_water_management_use_lime": random_bool(),
            "land_water_management_soil_testing": random_bool(),
            "land_water_management_undertake_irrigation": random_bool(),
            "land_water_management_irrigation_type": random.choice(irrigation_types),
            "land_water_management_irrigation_source": random.choice(irrigation_sources),
            "land_water_management_total_irrigated_area": round(random.uniform(0.1, 1000.0), 2),
            "land_water_management_type_of_irrigation_project": random.choice(irrigation_projects),
            "land_water_management_type_of_irrigation_project_name": "Project-"
            + "".join(random.choices(string.ascii_uppercase + string.digits, k=5)),
            "land_water_management_implementing_body": random.choice(management_implementing_bodies),
            "land_water_management_irrigation_scheme_membership": random.choice(scheme_memberships),
            "financial_services_percentage_of_income_from_farming": round(random.uniform(0.1, 1000.0), 2),
            "financial_services_vulnerable_marginalized_group": random_bool(),
            "financial_services_faith_based_organization": random_bool(),
            "financial_services_community_based_organization": random_bool(),
            "financial_services_producer_group": random_bool(),
            "financial_services_marketing_group": random_bool(),
            "financial_services_table_banking_group": random_bool(),
            "financial_services_common_interest_group": random_bool(),
            "financial_services_mobile_money_saving_loans": random_bool(),
            "financial_services_farmer_organization": random_bool(),
            "financial_services_other_money_lenders": random_bool(),
            "financial_services_self_salary_or_savings": random_bool(),
            "financial_services_family": random_bool(),
            "financial_services_commercial_bank": random_bool(),
            "financial_services_business_partners": random_bool(),
            "financial_services_savings_credit_groups": random_bool(),
            "financial_services_cooperatives": random_bool(),
            "financial_services_micro_finance_institutions": random_bool(),
            "financial_services_non_governmental_donors": random_bool(),
            "financial_services_crop_insurance": random_bool(),
            "financial_services_livestock_insurance": random_bool(),
            "financial_services_fish_insurance": random_bool(),
            "financial_services_farm_building_insurance": random_bool(),
            "financial_services_written_farm_records": random_bool(),
            "financial_services_main_source_of_information_on_good_agricultu": random.choice(main_source_informations),
            "financial_services_mode_of_extension_service": random.choice(extension_services),
            "financial_services_main_extension_service_provider": random.choice(implementing_bodies),
        }

        return farm_details_data

    def _get_species_data(self, species_type=None):
        # Generate random data for the fields not provided

        aqua_data = [
            "species_aqua_african_carp",
            "species_aqua_crabs",
            "species_aqua_shellfish",
            "species_aqua_other",
        ]
        crop_data = [
            "species_crop_aloe",
            "species_crop_apricots",
            "species_crop_arrow_root",
            "species_crop_cabbages",
        ]
        livestock_data = [
            "species_live_aberdeen_angus_cattle",
            "species_live_fleckvieh_cattle",
            "species_live_guernsey_cattle",
            "species_live_ear_lope_rabbit",
        ]

        if species_type == "aquaculture":
            species_data = random.choice(aqua_data)
        elif species_type == "crop":
            species_data = random.choice(crop_data)
        else:
            species_data = random.choice(livestock_data)

        return self.env.ref(f"spp_farmer_registry_demo.{species_data}")

    def _get_machinery_type_data(self):
        machinery_types = self.env["machinery.type"].search([]).mapped("id")
        machinery_type_id = random.choice(machinery_types)

        return machinery_type_id

    def _get_asset_type_data(self):
        asset_types = self.env["asset.type"].search([]).mapped("id")
        asset_type_id = random.choice(asset_types)

        return asset_type_id
