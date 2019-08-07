import jsonschema
import requests

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_rq import job

from common.util import email_user
from openldap.schemas.project.activate_project import activate_project_json
from openldap.schemas.project.create_project import create_project_json
from openldap.schemas.project.get_project import get_project_json
from openldap.schemas.project.list_projects import list_projects_json
from openldap.util import decode_response
from openldap.util import raise_for_data_error
from openldap.util import verify_payload_data
from common.util import email_user


@job
def list_projects():
    """
    List all OpenLDAP projects.
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, list_projects_json)
        raise_for_data_error(response.get('data'))
        return response
    except Exception as e:
        raise e


@job
def get_project(project_code):
    """
    Get an existing OpenLDAP project.

    Args:
        project_code (str): Project code - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/', project_code, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, get_project_json)
        raise_for_data_error(response.get('data'))
        return response
    except Exception as e:
        raise e


@job
def create_project(project, notify_user=True):
    """
    Create an OpenLDAP project.

    Args:
        project (Project): Project instance - required
        notify_user (bool): Issue a notification email to the project technical lead? - optional
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/'])
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    title = '{title} (Project Leader = {supervisor}, Technical Lead = {tech_lead})'.format(
        supervisor=project.supervisor_name,
        tech_lead=project.tech_lead.email,
        title=project.title,
    )
    payload = {
        'code': project.code,
        'category': project.category.id,
        'title': title,
        'technical_lead': project.tech_lead.profile.scw_username,
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
        jsonschema.validate(response, create_project_json)
        data = response.get('data')
        raise_for_data_error(data)
        mapping = {
            'code': 'cn',
            'technical_lead': 'memberUid',
        }
        verify_payload_data(payload, data, mapping)

        # Update project details.
        project.gid_number = data.get('gidNumber', '')
        project.save()

        if notify_user:
            subject = _(
                '{company_name} Project {code} Created'.format(
                    company_name=settings.COMPANY_NAME,
                    code=project.code,
                )
            )
            context = {
                'first_name': project.tech_lead.first_name,
                'to': project.tech_lead.email,
                'code': project.code,
                'status': project.get_status_display().lower(),
            }
            text_template_path = 'notifications/project/update.txt'
            html_template_path = 'notifications/project/update.html'
            email_user(subject, context, text_template_path, html_template_path)
        return response
    except Exception as e:
        if 'Existing Project' not in str(e):
            project.reset_status()
        raise e


@job
def deactivate_project(project, notify_user=True):
    """
    Deactivate an OpenLDAP project.

    Args:
        code (str): Project code - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/', project.code, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.delete(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()

        if notify_user:
            subject = _(
                '{company_name} Project {code} Deactivated'.format(
                    company_name=settings.COMPANY_NAME,
                    code=project.code,
                )
            )
            context = {
                'first_name': project.tech_lead.first_name,
                'to': project.tech_lead.email,
                'code': project.code,
                'status': project.get_status_display().lower(),
            }
            text_template_path = 'notifications/project/update.txt'
            html_template_path = 'notifications/project/update.html'
            email_user(subject, context, text_template_path, html_template_path)
        return response
    except Exception as e:
        project.reset_status()
        raise e


@job
def activate_project(project, notify_user=True):
    """
    Activate an OpenLDAP project.

    Args:
        code (str): Project code - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/enable/', project.code, '/'])
    headers = {'Cache-Control': 'no-cache'}
    try:
        response = requests.put(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        response = decode_response(response)
        jsonschema.validate(response, activate_project_json)
        raise_for_data_error(response.get('data'))

        if notify_user:
            subject = _(
                '{company_name} Project {code} Activated'.format(
                    company_name=settings.COMPANY_NAME,
                    code=project.code,
                )
            )
            context = {
                'first_name': project.tech_lead.first_name,
                'to': project.tech_lead.email,
                'code': project.code,
                'status': project.get_status_display().lower(),
            }
            text_template_path = 'notifications/project/update.txt'
            html_template_path = 'notifications/project/update.html'
            email_user(subject, context, text_template_path, html_template_path)
        return response
    except Exception as e:
        project.reset_status()
        raise e
