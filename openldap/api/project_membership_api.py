import jsonschema
import logging
import requests

from django_rq import job

from django.conf import settings

from openldap import schemas
from openldap.util import decode_response


@job
def create_project_membership(code, user_id):
    """
    Create a project membership.

    Args:
        code (str): Project code (prefix_00001) - required
        user_id (str): (prefix.username) - required
    """
    raise NotImplementedError('Not yet implemented.')


@job
def update_project_membership(code, user_id, status):
    """
    Update an existing project membership.

    Args:
        code (str): Project code (prefix_00001) - required
        user_id (str): (prefix.username) - required
        status (str) : Project membership status [revoked, suspended, authorised] - required
    """
    raise NotImplementedError('Not yet implemented.')


@job
def delete_project_membership(code, user_id):
    """
    Delete a project membership.

    Args:
        code (str): Project code (prefix_00001) - required
        user_id (str): (prefix.username) - required
    """
    raise NotImplementedError('Not yet implemented.')
