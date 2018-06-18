import jsonschema
import requests

from django.conf import settings
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django_rq import job

from openldap.schemas.user.activate_user import activate_user_json
from openldap.schemas.user.create_user import create_user_json
from openldap.schemas.user.get_user import get_user_json
from openldap.schemas.user.list_users import list_users_json
from openldap.schemas.user.reset_user_password import reset_user_password_json
from openldap.util import decode_response
from openldap.util import email_user
from openldap.util import raise_for_data_error
from openldap.util import verify_payload_data


def update_user_openldap_account(profile):
    """
    Ensure account status updates are propogated to the user's Open LDAP account.
    """
    if profile.account_status == profile.APPROVED:
        if profile.scw_username:
            activate_user_account.delay(user=profile.user)
        else:
            create_user.delay(user=profile.user)
    else:
        deactivate_user_account.delay(user=profile.user)


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
        jsonschema.validate(response, list_users_json)
        raise_for_data_error(response.get('data'))
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
        'firstName': user.first_name,
        'surname': user.last_name,
    }
    if user.profile.phone:
        payload.update({'telephone': user.profile.phone})
    if user.profile.uid_number:
        payload.update({'uidNumber': user.profile.uid_number})
    if hasattr(user.profile, 'department'):
        payload.update({'department': user.profile.department})
    try:
        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, create_user_json)
        data = response.get('data')
        raise_for_data_error(data)
        mapping = {
            'email': 'mail',
            'firstName': 'givenname',
        }
        verify_payload_data(payload, data, mapping)

        # Update user profile.
        user.profile.scw_username = data.get('uid', '')
        user.profile.uid_number = data.get('uidnumber', '')
        user.save()

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
    Get an existing user's OpenLDAP account details by user id.

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
        jsonschema.validate(response, get_user_json)
        raise_for_data_error(response.get('data'))
        return response
    except Exception as e:
        raise e


@job
def get_user_by_email_address(email_address):
    """
    Get an existing user's OpenLDAP account details by email address.

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
        jsonschema.validate(response, get_user_json)
        raise_for_data_error(response.get('data'))
        return response
    except Exception as e:
        raise e


@job
def reset_user_password(user, password, notify_user=True):
    """
    Reset a user's OpenLDAP account password.

    Args:
        user (CustomUser): User instance - required
        password (str): New password - required
        notify_user (bool): Issue a notification email to the user? - optional
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
            data=payload,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, reset_user_password_json)
        raise_for_data_error(response.get('data'))

        if notify_user:
            subject = _('{company_name} Password Reset'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': user.first_name,
                'to': user.email,
            }
            text_template_path = 'notifications/password_reset.txt'
            html_template_path = 'notifications/password_reset.html'
            email_user(subject, context, text_template_path, html_template_path)
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
        jsonschema.validate(response, activate_user_json)
        raise_for_data_error(response.get('data'))

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
