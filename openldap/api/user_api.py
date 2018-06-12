import jsonschema
import requests

from django_rq import job

from django.conf import settings
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from openldap.schemas.activate_account import activate_account_json
from openldap.schemas.create_user import create_user_json
from openldap.schemas.deactivate_account import deactivate_account_json
from openldap.schemas.get_user import get_user_json
from openldap.schemas.list_users import list_users_json
from openldap.schemas.reset_password import reset_password_json
from openldap.util import decode_response
from openldap.util import email_user


def _verify_payload_data(payload, data, mapping):
    """
    Ensure data values match in both the payload and data dict's.
    """
    for payload_key, data_key in mapping.items():
        if payload[payload_key] != data[data_key]:
            message = 'Data Mismatch payload[{payload_key}] != data[{data_key}]'.format(
                payload_key=payload_key,
                data_key=data_key,
            )
            raise ValueError(message)


def _update_user_profile(user, data):
    """
    Update the user's profile.
    """
    user.profile.scw_username = data['uid']
    user.profile.uid_number = data['uidnumber']
    user.save()


def _error_check(data):
    """
    Check for data errors.
    """
    if data.get('error', None):
        raise ValueError('Error Detected: {error}'.format(error=data['error']))


@job
def list_users():
    """
    List all users.
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, list_users_json)
    except Exception as e:
        raise e
    return response


@job
def create_user(user, notify_user=True):
    """
    Create an OpenLDAP user account.

    Args:
        user (CustomUser): User instance - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/'])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {
        'email': user.email,
        'title': 'TODO',
        'firstName': user.first_name,
        'surname': user.last_name,
        'telephone': user.profile.phone,
        'uidNumber': user.profile.uid_number,
    }
    try:
        payload.update({'department': user.profile.department})
    except Exception:
        # Optional field, so ignore if not present
        pass

    try:
        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, create_user_json)

        mapping = {
            'email': 'mail',
            'firstName': 'givenname',
            'uidNumber': 'uidnumber',
        }
        _verify_payload_data(payload, response.get('data'), mapping)
        _update_user_profile(user, response.get('data'))

        if notify_user:
            subject = _('{company_name} Account Created'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': user.first_name,
                'to': user.email,
            }
            text_template_path = 'notifications/account_status_update.txt'
            html_template_path = 'notifications/account_status_update.html'
            email_user(subject, context, text_template_path, html_template_path)
    except Exception as e:
        if 'Existing user' not in str(e):
            user.profile.reset_account_status()
        raise e
    return response


@job
def get_user_by_id(user_id):
    """
    Get an existing user by id.

    Args:
        user_id (str): User id - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/', user_id, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, get_user_json)
    except Exception as e:
        raise e
    return response


@job
def get_user_by_email_address(email_address):
    """
    Get an existing user by email address.

    Args:
        email_address (str): Email address - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/', email_address, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, get_user_json)
    except Exception as e:
        raise e
    return response


@job
def reset_user_password(email_address, password):
    """
    Reset a user's password.

    Args:
        email_address (str): Email address - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/resetPassword/', email_address, '/'])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {'password': password}
    try:
        response = requests.post(
            url,
            headers=headers,
            params=payload,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, reset_password_json)
    except Exception as e:
        raise e
    return response


@job
def deactivate_user_account(user, notify_user=True):
    """
    Deactivate an existing user's OpenLDAP account.

    Args:
        user (CustomUser): User instance - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/', user.email, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.delete(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, deactivate_account_json)

        if notify_user:
            subject = _('{company_name} Account Deactivated'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': user.first_name,
                'to': user.email,
            }
            text_template_path = 'notifications/account_deactivated.txt'
            html_template_path = 'notifications/account_deactivated.html'
            email_user(subject, context, text_template_path, html_template_path)
    except Exception as e:
        user.profile.reset_account_status()
        raise e
    return response


@job
def activate_user_account(user, notify_user=True):
    """
    Activate an existing user's OpenLDAP account.

    Args:
        user (CustomUser): User instance - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/enable/', user.email, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.put(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)

        _error_check(response.get('data'))
        jsonschema.validate(response, activate_account_json)

        if notify_user:
            subject = _('{company_name} Account Activated'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': user.first_name,
                'to': user.email,
            }
            text_template_path = 'notifications/account_activated.txt'
            html_template_path = 'notifications/account_activated.html'
            email_user(subject, context, text_template_path, html_template_path)
    except Exception as e:
        user.profile.reset_account_status()
        raise e
    return response
