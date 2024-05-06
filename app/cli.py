from argparse import ArgumentParser

from app.source import generate_fake_companies
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

group_names = ['Administrators']
application_names = ['Fossa', 'Verdant', 'Yabby']
administrator_role_name = 'administrator'


def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument('api_key', help="FusionAuth API Key.")
    parser.add_argument('key_master_id', help="FusionAuth Key Master ID.")
    args = parser.parse_args()
    print("Hello, %s!" % args.api_key)
    print("Hello, %s!" % args.key_master_id)

    companies = generate_fake_companies()


if __name__ == '__main__':
    main()
