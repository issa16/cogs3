import jsonschema
import logging
import requests

from django_rq import job

from django.conf import settings

from openldap import schemas
from openldap.util import decode_response


@job
def list_projects():
    """
    List all projects.
    """
    raise NotImplementedError('Not yet implemented.')


@job
def create_project(code, category, title, technical_lead):
    """
    Create a project.

    Args:
        code (str): Project code (prefix_00001) - required
        category (str): Project category [1,2,3,4,5] - required
        title (str): Project title - required
        technical_lead (str): Project technical lead - required
    """
    raise NotImplementedError('Not yet implemented.')


@job
def update_project(code, status):
    """
    Update an existing project.

    Args:
        code (str): Project code (prefix_00001) - required
        status (str): Project status [revoked, suspended, closed, approved] - required
    """
    raise NotImplementedError('Not yet implemented.')


@job
def delete_project(code):
    """
    Delete a project.

    Args:
        code (str): Project code (prefix_00001) - required
    """
    raise NotImplementedError('Not yet implemented.')
