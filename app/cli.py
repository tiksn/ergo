import logging
from argparse import ArgumentParser

from app.source import generate_fake_companies
from app.target import populate_target

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument('api_key', help="FusionAuth API Key.")
    args = parser.parse_args()

    api_key = args.api_key

    companies = generate_fake_companies()
    populate_target(api_key, companies, None, None)


if __name__ == '__main__':
    main()
