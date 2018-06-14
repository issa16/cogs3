import jsonschema
import requests

from django.conf import settings
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django_rq import job

from openldap.schemas.activate_account import activate_account_json
from openldap.schemas.create_user import create_user_json
from openldap.schemas.get_user import get_user_json
from openldap.schemas.list_users import list_users_json
from openldap.schemas.reset_password import reset_password_json
from openldap.util import decode_response
from openldap.util import email_user
from openldap.util import raise_for_data_error
from openldap.util import verify_payload_data


def _update_user_profile(user, data):
    """
    Update the user's profile.
    """
    user.profile.scw_username = data['uid']
    user.profile.uid_number = data['uidnumber']
    user.save()


@job
def list_users():
    """
    List all OpenLDAP user accounts.
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
        data = response.get('data', {})

        raise_for_data_error(data)
        jsonschema.validate(response, list_users_json)

        return response
    except Exception as e:
        raise e


@job
def create_user(user, notify_user=True):
    """
    Create an OpenLDAP user account.

    Args:
        user (CustomUser): User instance - required
        notify_user (bool): Issue a notification email to the user? - optional
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/'])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {
        'email': user.email,
        'title': 'Mx',
        'firstName': user.first_name,
        'surname': user.last_name,
    }
    if user.profile.phone:
        payload.update({'telephone': user.profile.phone})
    if user.profile.uid_number:
        payload.update({'uidNumber': user.profile.uid_number})
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
        data = response.get('data', {})

        raise_for_data_error(data)
        jsonschema.validate(response, create_user_json)

        mapping = {
            'email': 'mail',
            'firstName': 'givenname',
            'title': 'title',
        }
        verify_payload_data(payload, data, mapping)
        _update_user_profile(user, data)

        if notify_user:
            subject = _('{company_name} Account Created'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': user.first_name,
                'to': user.email,
            }
            text_template_path = 'notifications/account_created.txt'
            html_template_path = 'notifications/account_created.html'
            email_user(subject, context, text_template_path, html_template_path)

        return response
    except Exception as e:
        if 'Existing user' not in str(e):
            user.profile.reset_account_status()
        raise e


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
        data = response.get('data', {})

        raise_for_data_error(data)
        jsonschema.validate(response, get_user_json)

        return response
    except Exception as e:
        raise e


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
        data = response.get('data', {})

        raise_for_data_error(data)
        jsonschema.validate(response, get_user_json)

        return response
    except Exception as e:
        raise e


def reset_user_password(user, password):
    """
    Reset a user's OpenLDAP acccount password.

    Args:
        user (CustomUser): User instance - required
        password (str): New password - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'user/resetPassword/', user.email, '/'])
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
        data = response.get('data', {})

        raise_for_data_error(data)
        jsonschema.validate(response, reset_password_json)

        return response
    except Exception as e:
        raise e


@job
def deactivate_user_account(user, notify_user=True):
    """
    Deactivate an existing user's OpenLDAP account.

    Args:
        user (CustomUser): User instance - required
        notify_user (bool): Issue a notification email to the user? - optional
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

        if notify_user:
            subject = _('{company_name} Account Deactivated'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': user.first_name,
                'to': user.email,
            }
            text_template_path = 'notifications/account_deactivated.txt'
            html_template_path = 'notifications/account_deactivated.html'
            email_user(subject, context, text_template_path, html_template_path)

        return response
    except Exception as e:
        user.profile.reset_account_status()
        raise e


@job
def activate_user_account(user, notify_user=True):
    """
    Activate an existing user's OpenLDAP account.

    Args:
        user (CustomUser): User instance - required
        notify_user (bool): Issue a notification email to the user? - optional
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
        data = response.get('data', {})

        raise_for_data_error(data)
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

        return response
    except Exception as e:
        user.profile.reset_account_status()
        raise e
