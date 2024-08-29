import logging
from argparse import ArgumentParser

from app.source import generate_fake_companies
from app.target import populate_target

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    parser = ArgumentParser(prog='cli')
    parser.add_argument('api_key', help="FusionAuth API Key.")
    parser.add_argument('base_url', help="FusionAuth URL.")
    args = parser.parse_args()

    api_key = args.api_key
    base_url = args.base_url

    companies = generate_fake_companies()
    applications = {
        'Fossa': {
            'Web': {
                'RedirectURLs': [
                    'http://*.localtest.me:4210/',
                    'http://*.dev.localtest.me:4211/',
                    'http://*.test.localtest.me:4212/'
                ]
            },
            'Native': {
                'RedirectURLs': [
                    'http://127.0.0.1/native-app',
                ]
            },
        },
        'Verdant': {
            'Web': {
                'RedirectURLs': [
                    'http://*.localtest.me:4220/',
                    'http://*.dev.localtest.me:4221/',
                    'http://*.test.localtest.me:4222/'
                ]
            },
            'Native': {
                'RedirectURLs': [
                    'http://127.0.0.1/native-app',
                ]
            },
        },
        'Yabby': {
            'Web': {
                'RedirectURLs': [
                    'http://*.localtest.me:4230/',
                    'http://*.dev.localtest.me:4231/',
                    'http://*.test.localtest.me:4232/'
                ]
            },
            'Native': {
                'RedirectURLs': [
                    'http://127.0.0.1/native-app',
                ]
            },
        },
    }
    populate_target(api_key, base_url, companies, applications)


if __name__ == '__main__':
    main()
