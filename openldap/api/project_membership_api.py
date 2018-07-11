import jsonschema
import requests

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_rq import job

from openldap.schemas.project_membership.create_project_membership import create_project_membership_json
from openldap.schemas.project_membership.delete_project_membership import delete_project_membership_json
from openldap.schemas.project_membership.list_project_memberships import list_project_memberships_json
from openldap.util import decode_response
from openldap.util import email_user
from openldap.util import raise_for_data_error


@job
def list_project_memberships(project_code):
    """
    List all OpenLDAP project memberships for a given project.
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/member/', project_code, '/'])
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, list_project_memberships_json)
        raise_for_data_error(response.get('data'))
        return response
    except Exception as e:
        raise e


@job
def create_project_membership(project_membership, notify_user=True):
    """
    Create an OpenLDAP project membership.

    Args:
        project_membership (str): Project Membership - required
        notify_user (bool): Issue a notification email to the user? - optional
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/member/', project_membership.project.code, '/'])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {
        'email': project_membership.user.email,
    }
    try:
        response = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, create_project_membership_json)
        raise_for_data_error(response.get('data'))

        if notify_user:
            subject = _('{company_name} Project Membership Created'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': project_membership.user.first_name,
                'to': project_membership.user.email,
                'code': project_membership.project.code,
                'status': project_membership.get_status_display().lower(),
            }
            text_template_path = 'notifications/project_membership/update.txt'
            html_template_path = 'notifications/project_membership/update.html'
            email_user(subject, context, text_template_path, html_template_path)
        return response
    except Exception as e:
        project_membership.reset_status()
        raise e


@job
def delete_project_membership(project_membership, notify_user=True):
    """
    Delete an OpenLDAP project membership.

    Args:
        project_membership (str): Project Membership - required
        notify_user (bool): Issue a notification email to the user? - optional
    """
    url = ''.join([
        settings.OPENLDAP_HOST, 'project/member/', project_membership.project.code, '/', project_membership.user.email,
        '/'
    ])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.delete(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, delete_project_membership_json)
        raise_for_data_error(response.get('data'))

        if notify_user:
            subject = _('{company_name} Project Membership Deleted'.format(company_name=settings.COMPANY_NAME))
            context = {
                'first_name': project_membership.user.first_name,
                'to': project_membership.user.email,
                'code': project_membership.project.code,
                'status': project_membership.get_status_display().lower(),
            }
            text_template_path = 'notifications/project_membership/update.txt'
            html_template_path = 'notifications/project_membership/update.html'
            email_user(subject, context, text_template_path, html_template_path)
        return response
    except Exception as e:
        project_membership.reset_status()
        raise e
