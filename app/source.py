import re
import uuid

from faker import Faker
from faker.providers import company
import logging


def populate_company_slugs(companies):
    company_slugs = set({})
    for company_id, company in companies.items():
        company_name = company["name"]
        company_slug = "".join(e[0] for e in company_name.replace("-", " ").split()).lower()
        company["slug"] = company_slug
        if company_slug in company_slugs:
            raise Exception(F"Slug {company_slug} was already populated")
        else:
            company_slugs.add(company_slug)


def generate_fake_companies():
    fake = Faker()
    fake.add_provider(company)
    Faker.seed(693013693)
    companies = {}
    for company_index in range(fake.random_int(10, 15)):
        company_id = uuid.UUID(fake.uuid4())
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

        employee_indices = range(fake.random_int(company_index * 2 + 1, company_index * 8 + 1))
        for employee_index in employee_indices:
            employee_id = uuid.UUID(fake.uuid4())

            is_first_employee = employee_index == 0
            is_first_10percent_employee = (employee_index + 1) <= (len(employee_indices) / 10)
            is_administrator = is_first_employee or is_first_10percent_employee

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
                "is_administrator": is_administrator,
                "mobile_phone": employee_mobile_phone,
                "first_name": employee_first_name,
                "middle_name": employee_middle_name,
                "last_name": employee_last_name,
                "full_name": employee_full_name,
            }

            logging.info(f"{employee_index + 1}: {{{employee_id}}} {employee_full_name} <{employee_email}>")

    populate_company_slugs(companies)

    return companies
