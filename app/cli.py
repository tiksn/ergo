from argparse import ArgumentParser

from app.source import generate_fake_companies
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

group_names = ['Administrators']
application_names = ['Fossa', 'Verdant', 'Yabby']
administrator_role_name = 'administrator'


def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument('name', help="The user's name.")
    args = parser.parse_args()
    print("Hello, %s!" % args.name)

    companies = generate_fake_companies()


if __name__ == '__main__':
    main()
