import re

from faker import Faker
from faker.providers import company
import logging


def generate_fake_companies():
    fake = Faker()
    fake.add_provider(company)
    Faker.seed(693013693)
    companies = {}
    for company_index in range(fake.random_int(10, 15)):
        company_id = fake.uuid4()
        company_name = fake.company()

        company_host_main_domain = re.sub(r"[^a-zA-Z0-9]+", "", company_name).lower()
        company_host = f"{company_host_main_domain}.com"

        companies[company_id] = {
            "id": company_id,
            "name": company_name,
            "host": company_host,
            "employees": {},
        }

        logging.info(f"{{{company_id}}} {company_name}")

        for employee_index in range(fake.random_int(company_index * 2 + 1, company_index * 8 + 1)):
            employee_id = fake.uuid4()

            is_male = fake.boolean()

            employee_first_name = fake.first_name_male() if is_male else fake.first_name_female()

            employee_middle_name = fake.first_name_male() if is_male else fake.first_name_female()
            employee_middle_name = employee_middle_name if fake.boolean() else None

            employee_prefix = fake.prefix_male() if is_male else fake.prefix_female()
            employee_prefix = employee_prefix if fake.boolean() else None

            employee_suffix = fake.suffix_male() if is_male else fake.suffix_female()
            employee_suffix = employee_suffix if fake.boolean() else None

            employee_last_name = fake.last_name_male() if is_male else fake.last_name_female()

            employee_full_name = f"{employee_first_name} {employee_middle_name} {employee_last_name}" if employee_middle_name is not None else f"{employee_first_name} {employee_last_name}"
            employee_full_name = f"{employee_prefix} {employee_full_name}" if employee_prefix is not None else employee_full_name
            employee_full_name = f"{employee_full_name} {employee_suffix}" if employee_suffix is not None else employee_full_name

            employee_username = re.sub(r"[^a-zA-Z0-9]+", "", f"{employee_first_name} {employee_last_name}").lower()
            employee_email = f"{employee_username}@{company_host}"

            employee_mobile_phone = fake.phone_number()
            companies[company_id]["employees"][employee_id] = {
                "id": employee_id,
                "username": employee_username,
                "email": employee_email,
                "mobile_phone": employee_mobile_phone,
                "first_name": employee_first_name,
                "middle_name": employee_middle_name,
                "last_name": employee_last_name,
                "full_name": employee_full_name,
            }

            logging.info(f"{employee_index + 1}: {{{employee_id}}} {employee_full_name} <{employee_email}>")

    return companies
