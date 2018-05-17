import jsonschema
import logging
import requests

from django.conf import settings

from openldap import schemas
from openldap.decorators import OpenLDAPException
from openldap.util import decode_response

logger = logging.getLogger('openldap')


@OpenLDAPException(logger)
def list_projects():
    """
    List all projects.
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/'])
    logger.info('OpenLDAP Project API :: GET ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.get(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    # TODO - Pending implementation
    # jsonschema.validate(response, schemas.list_projects_schema)
    return response


@OpenLDAPException(logger)
def create_project(code, category, title, technical_lead):
    """
    Create a project.

    Args:
        code (str): Project code (prefix_00001) - required
        category (str): Project category [1,2,3,4,5] - required
        title (str): Project title - required
        technical_lead (str): Project technical lead (prefix.username) - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/'])
    logger.info('OpenLDAP Project API :: POST ::', url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {
        'code': code,
        'category': category,
        'title': title,
        'technical_lead': technical_lead,
    }
    response = requests.post(
        url,
        headers=headers,
        params=payload,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    # TODO - Pending implementation
    # jsonschema.validate(response, schemas.create_project_schema)
    return response


@OpenLDAPException(logger)
def update_project(code, status):
    """
    Update an existing project.

    Args:
        code (str): Project code (prefix_00001) - required
        status (str): Project status [revoked, suspended, closed, approved] - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/', code, '/'])
    logger.info('OpenLDAP Project API :: PUT ::', url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    payload = {
        'code': code,
        'status': status,
    }
    response = requests.post(
        url,
        headers=headers,
        params=payload,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    # TODO - Pending implementation
    # jsonschema.validate(response, schemas.update_project_schema)
    return response


@OpenLDAPException(logger)
def delete_project(code):
    """
    Delete a project.

    Args:
        code (str): Project code (prefix_00001) - required
    """
    url = ''.join([settings.OPENLDAP_HOST, 'project/', code, '/'])
    logger.info('OpenLDAP Project API :: DELETE ::', url)
    headers = {'Cache-Control': 'no-cache'}
    response = requests.delete(
        url,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    response = decode_response(response)
    # TODO - Pending implementation
    #jsonschema.validate(response, schemas.delete_project_schema)
    return response
