import logging
import uuid

from fusionauth.fusionauth_client import FusionAuthClient


def populate_target(api_key: str, base_url: str, companies, applications):
    client = FusionAuthClient(api_key, base_url)

    group_names = ['Administrators']
    administrator_role_name = 'administrator'
    main_key_id = uuid.UUID('a3aee1ec-c965-4ec8-97b2-c0245bc1c5ec')
    main_key_name = 'MainKey'

    create_or_update_key(client, main_key_id, main_key_name)

    for _, company in companies.items():
        create_or_update_tenant(client, company, main_key_id)

    create_or_update_admin_users(client)

    for _, company in companies.items():
        client.set_tenant_id(str(company['id']))
        administrator_role_ids = []

        for application_name, idioms in applications.items():
            for idiom_name, idiom_info in idioms.items():
                application_id = uuid.uuid5(company['id'], f"application-{application_name}-{idiom_name}")
                administrator_role_id = uuid.uuid5(application_id, f"role-{administrator_role_name}")
                administrator_role_ids.append(str(administrator_role_id))

                create_or_update_application(
                    client,
                    company,
                    application_id,
                    application_name,
                    idiom_name,
                    idiom_info,
                    administrator_role_id,
                    administrator_role_name)

        for group_name in group_names:
            group_id = uuid.uuid5(company['id'], f"group-{group_name}")

            create_or_update_group(client, group_id, group_name, administrator_role_ids)

    for _, company in companies.items():
        client.set_tenant_id(str(company['id']))

        for _, employee in company['employees'].items():
            create_or_update_user(client, company['id'], employee)

            for application_name, idioms in applications.items():
                for idiom_name, idiom_info in idioms.items():
                    application_id = uuid.uuid5(company['id'], f"application-{application_name}-{idiom_name}")

                    create_or_update_registration(client, company['id'], employee['id'], application_id, [])

            for group_name in group_names:
                group_id = uuid.uuid5(company['id'], f"group-{group_name}")

                create_or_update_members(client, group_id, employee)


def create_or_update_admin_users(client):
    default_tenant_id = uuid.UUID('4be75029-1365-d0e4-0bb8-34c58aac6745')
    default_application_id = uuid.UUID('3c219e58-ed0e-4b18-ad48-f4f92793ae32')
    global_admin_role_name = "admin"
    default_tenant_user_1_id = uuid.UUID('104ec185-c7a7-4601-9102-5e1feaa20d36')
    default_tenant_user_2_id = uuid.UUID('1dbaa896-b27f-4888-9b55-4d172f71a80b')
    default_tenant_admin_users = {
        default_tenant_user_1_id: {
            "id": default_tenant_user_1_id,
            "username": "tiksn",
            "email": "tigran.torosyan@tiksn.am",
            "is_administrator": True,
            "mobile_phone": "+15559374192",
            "first_name": "Tigran",
            "middle_name": "TIKSN",
            "last_name": "Torosyan",
            "full_name": "Tigran TIKSN Torosyan",
        },
        default_tenant_user_2_id: {
            "id": default_tenant_user_2_id,
            "username": "ashotnazaryan",
            "email": "ashot@nazaryan.am",
            "is_administrator": True,
            "mobile_phone": "+15559374182",
            "first_name": "Ashot",
            "middle_name": "",
            "last_name": "Nazaryan",
            "full_name": "Ashot Nazaryan",
        }
    }
    client.set_tenant_id(str(default_tenant_id))
    for _, employee in default_tenant_admin_users.items():
        create_or_update_user(client, default_tenant_id, employee)
        create_or_update_registration(client, default_tenant_id, employee['id'], default_application_id,
                                      [global_admin_role_name])


def create_or_update_members(client: FusionAuthClient,
                             group_id: uuid.UUID,
                             employee):
    if employee['is_administrator']:
        members_request = {
            'members': {
                str(group_id): [
                    {
                        'userId': str(employee['id'])
                    },
                ]
            },
        }

        create_members_response = client.create_group_members(members_request)
        if create_members_response.was_successful():
            logging.info(create_members_response.success_response)
        else:
            logging.error(create_members_response.error_response)


def create_or_update_registration(client: FusionAuthClient,
                                  company_id: uuid.UUID,
                                  user_id: uuid.UUID,
                                  application_id: uuid.UUID,
                                  roles: []):
    registration_request = {
        'skipRegistrationVerification': True,
        'registration': {
            'tenantId': str(company_id),
            'applicationId': str(application_id),
            'roles': roles,
        }
    }
    retrieve_registration_response = client.retrieve_registration(str(user_id), str(application_id))
    if retrieve_registration_response.was_successful():

        update_registration_response = client.update_registration(str(user_id), registration_request)
        if update_registration_response.was_successful():
            logging.info(update_registration_response.success_response)
        else:
            logging.error(update_registration_response.error_response)
    else:

        create_registration_response = client.register(registration_request, str(user_id))
        if create_registration_response.was_successful():
            logging.info(create_registration_response.success_response)
        else:
            logging.error(create_registration_response.error_response)


def create_or_update_user(client: FusionAuthClient, company_id: uuid.UUID, employee):
    user_request = {
        'sendSetPasswordEmail': False,
        'skipVerification': True,
        'user': {
            'tenantId': str(company_id),
            'username': employee['username'],
            'email': employee['email'],
            'password': 'Tiksn.com#1',
            'firstName': employee['first_name'],
            'middleName': employee['middle_name'],
            'lastName': employee['last_name'],
            'fullName': employee['full_name'],
            'mobilePhone': employee['mobile_phone'],
            'imageUrl': '',
        }
    }
    retrieve_user_response = client.retrieve_user(str(employee['id']))
    if retrieve_user_response.was_successful():

        update_user_response = client.update_user(str(employee['id']), user_request)
        if update_user_response.was_successful():
            logging.info(update_user_response.success_response)
        else:
            logging.error(update_user_response.error_response)
    else:

        create_user_response = client.create_user(user_request, str(employee['id']))
        if create_user_response.was_successful():
            logging.info(create_user_response.success_response)
        else:
            logging.error(create_user_response.error_response)


def create_or_update_group(client: FusionAuthClient, group_id: uuid.UUID, group_name: str,
                           administrator_role_ids: list[str]):
    group_request = {
        'group': {
            'name': group_name
        },
        'roleIds': administrator_role_ids,
    }
    retrieve_group_response = client.retrieve_group(group_id)
    if retrieve_group_response.was_successful():

        update_group_response = client.update_group(group_id, group_request)
        if update_group_response.was_successful():
            logging.info(update_group_response.success_response)
        else:
            logging.error(update_group_response.error_response)

    else:

        create_group_response = client.create_group(group_request, group_id)
        if create_group_response.was_successful():
            logging.info(create_group_response.success_response)
        else:
            logging.error(create_group_response.error_response)


def create_or_update_application(client: FusionAuthClient,
                                 company,
                                 application_id: uuid.UUID,
                                 application_name: str,
                                 idiom_name: str,
                                 idiom_info: dict,
                                 administrator_role_id: uuid.UUID,
                                 administrator_role_name: str):
    application_display_name = f"{application_name} ({idiom_name})"
    redirectURLs = [redirectUrl.replace("*", company['slug']) for redirectUrl in idiom_info['RedirectUrlTemplates']]
    originURLs = [originUrl.replace("*", company['slug']) for originUrl in idiom_info['OriginUrlTemplates']]

    application_request = {
        'application': {
            'tenantId': str(company['id']),
            'name': application_display_name,
            'roles': [
                {
                    'id': str(administrator_role_id),
                    'name': administrator_role_name,
                    'description': f"'{administrator_role_name}' for '{application_name}' for '{idiom_name}'",
                    'isSuperRole': True,
                }
            ],
            'oauthConfiguration': {
                'authorizedRedirectURLs': redirectURLs,
                'authorizedOriginURLs': originURLs,
                'generateRefreshTokens': True,
                'proofKeyForCodeExchangePolicy': 'Required',
                'enabledGrants': ['authorization_code', 'refresh_token'],
            },
        }
    }
    retrieve_application_response = client.retrieve_application(application_id)
    if retrieve_application_response.was_successful():

        update_application_response = client.update_application(application_id, application_request)
        if update_application_response.was_successful():
            logging.info(update_application_response.success_response)
        else:
            logging.error(update_application_response.error_response)

    else:

        create_application_response = client.create_application(application_request, application_id)
        if create_application_response.was_successful():
            logging.info(create_application_response.success_response)
        else:
            logging.error(create_application_response.error_response)


def create_or_update_tenant(client: FusionAuthClient,
                            company,
                            key_id: uuid.UUID):
    tenant_request = {
        'tenant': {
            'name': company['name'],
            'jwtConfiguration': {
                'accessTokenKeyId': str(key_id),
                'idTokenKeyId': str(key_id),
            }
        }
    }

    retrieve_tenant_response = client.retrieve_tenant(str(company['id']))

    if retrieve_tenant_response.was_successful():

        update_tenant_response = client.update_tenant(str(company['id']), tenant_request)
        if update_tenant_response.was_successful():
            logging.info(update_tenant_response.success_response)
        else:
            logging.error(update_tenant_response.error_response)

    else:

        create_tenant_response = client.create_tenant(tenant_request, str(company['id']))
        if create_tenant_response.was_successful():
            logging.info(create_tenant_response.success_response)
        else:
            logging.error(create_tenant_response.error_response)


def create_or_update_key(client: FusionAuthClient,
                         key_id: uuid.UUID,
                         key_name: str):
    key_request = {
        'key': {
            'algorithm': 'RS256',
            'name': key_name,
            'length': 2048,
        }
    }
    retrieve_key_response = client.retrieve_key(str(key_id))
    if retrieve_key_response.was_successful():

        update_key_response = client.update_key(str(key_id), key_request)
        if update_key_response.was_successful():
            logging.info(update_key_response.success_response)
        else:
            logging.error(update_key_response.error_response)
    else:

        create_key_response = client.generate_key(key_request, str(key_id))
        if create_key_response.was_successful():
            logging.info(create_key_response.success_response)
        else:
            logging.error(create_key_response.error_response)
