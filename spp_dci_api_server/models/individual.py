from odoo import models


class SPPIndividualCustom(models.Model):
    _inherit = "res.partner"

    def get_dci_individual_registry_data(self):
        """
        The function `get_dci_individual_registry_data` retrieves individual registry data and returns
        it in a specific format.
        :return: a list of dictionaries, where each dictionary represents an individual's registry data.
        Each dictionary contains the following key-value pairs:
        """
        reg_records = []

        for rec in self:
            identifier = []
            for reg_id in rec.reg_ids:
                if reg_id.value and reg_id.id_type and reg_id.id_type.name:
                    identifier.append(
                        {
                            "name": reg_id.id_type.name,
                            "identifier": reg_id.value,
                        }
                    )
            if not identifier:
                continue

            phone_numbers = []
            for phone_number_id in rec.phone_number_ids:
                phone_numbers.append(
                    {
                        "phone": phone_number_id.phone_no,
                        "country": {
                            "id": phone_number_id.country_id.id,
                            "name": phone_number_id.country_id.name,
                            "code": phone_number_id.country_id.code,
                        }
                        if phone_number_id.country_id
                        else {},
                    }
                )

            households = []
            for membership_id in rec.individual_membership_ids:
                household = {}
                group = membership_id.group
                household["name"] = group.name

                hh_identifier = []
                for reg_id in group.reg_ids:
                    if reg_id.value and reg_id.id_type and reg_id.id_type.name:
                        hh_identifier.append(
                            {
                                "name": reg_id.id_type.name,
                                "identifier": reg_id.value,
                            }
                        )
                household["identifier"] = hh_identifier

                hh_phone_numbers = []
                for phone_number_id in group.phone_number_ids:
                    hh_phone_numbers.append(
                        {
                            "phone": phone_number_id.phone_no,
                            "country": {
                                "id": phone_number_id.country_id.id,
                                "name": phone_number_id.country_id.name,
                                "code": phone_number_id.country_id.code,
                            }
                            if phone_number_id.country_id
                            else {},
                        }
                    )
                household["phoneNumbers"] = hh_phone_numbers
                households.append(household)

            reg_records.append(
                {
                    "identifier": identifier,
                    "birthDate": str(rec.birthdate),
                    "givenName": rec.given_name,
                    "familyName": rec.family_name,
                    "sex": rec.gender.lower() if rec.gender else "",
                    "birthPlace": rec.birth_place,
                    "email": rec.email,
                    "phoneNumbers": phone_numbers,
                    "households": households,
                }
            )
        return reg_records
