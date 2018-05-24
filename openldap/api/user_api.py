import jsonschema
import logging
import requests

from django.conf import settings

from openldap.decorators import OpenLDAPException
from openldap.schemas.create_user import create_user_json
from openldap.schemas.delete_user import delete_user_json
from openldap.schemas.enable_account import enable_account_json
from openldap.schemas.get_user import get_user_json
from openldap.schemas.list_users import list_users_json
from openldap.schemas.reset_password import reset_password_json
from openldap.util import decode_response

logger = logging.getLogger('openldap')


@OpenLDAPException(logger)
def list_users():
    """
    List all users.
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/'])
    logger.info('OpenLDAP User API :: GET ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.get(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, list_users_json)
    return response


@OpenLDAPException(logger)
def create_user(email, title, first_name, surname, department, telephone, uid_number):
    """
    Create a User.

    Args:
        email (str): Email address - required
        title (str): Title - required
        first_name (str): First name - required
        surname (str): Surname - required
        department (str): Department - optional
        telephone (str): telephone - optional
        uid_number (str): Override uidNumber/gidNumber - optional
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/'])
    logger.info('OpenLDAP User API :: POST ::', url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {
        'email': email,
        'title': title,
        'firstName': first_name,
        'surname': surname,
    }
    if department:
        payload.update({'department': department})
    if telephone:
        payload.update({'telephone': telephone})
    if uid_number:
        payload.update({'uidNumber': uid_number})
    response = requests.post(
        url,
        headers=headers,
        params=payload,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, create_user_json)
    return response


@OpenLDAPException(logger)
def get_user_by_id(user_id):
    """
    Get an existing user by id.

    Args:
        user_id (str): User id - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/', user_id, '/'])
    logger.info('OpenLDAP User API :: GET ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.get(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, get_user_json)
    return response


@OpenLDAPException(logger)
def get_user_by_email_address(email_address):
    """
    Get an existing user by email address.

    Args:
        email_address (str): Email address - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/', email_address, '/'])
    logger.info('OpenLDAP User API :: GET ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.get(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, get_user_json)
    return response


@OpenLDAPException(logger)
def delete_user(email_address):
    """
    Delete (deactivate) an existing user.

    Args:
        email_address (str): Email address - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/', email_address, '/'])
    logger.info('OpenLDAP User API :: DELETE ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.delete(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, delete_user_json)
    return response


@OpenLDAPException(logger)
def reset_user_password(email_address, password):
    """
    Reset a user's password.

    Args:
        email_address (str): Email address - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/resetPassword/', email_address, '/'])
    logger.info('OpenLDAP User API :: POST ::', url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {'password': password}
    response = requests.post(
        url,
        headers=headers,
        params=payload,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, reset_password_json)
    return response


@OpenLDAPException(logger)
def enable_user_account(email_address):
    """
    Enable a user's account.

    Args:
        email_address (str): Email address - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/enable/', email_address, '/'])
    logger.info('OpenLDAP User API :: PUT ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.put(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    jsonschema.validate(response, enable_account_json)
    return response
