import jsonschema
import logging
import requests

from django.conf import settings

from openldap import schemas
from openldap.decorators import OpenLDAPException
from openldap.util import decode_response

logger = logging.getLogger('openldap')


@OpenLDAPException(logger)
def create_project_membership(code, user_id):
    """
    Create a project membership.

    Args:
        code (str): Project code (prefix_00001) - required
        user_id (str): (prefix.username) - required
    """
    raise NotImplementedError('Not yet implemented.')


@OpenLDAPException(logger)
def update_project_membership(code, user_id, status):
    """
    Update an existing project membership.

    Args:
        code (str): Project code (prefix_00001) - required
        user_id (str): (prefix.username) - required
        status (str) : Project membership status [revoked, suspended, authorised] - required
    """
    raise NotImplementedError('Not yet implemented.')


@OpenLDAPException(logger)
def delete_project_membership(code, user_id):
    """
    Delete a project membership.

    Args:
        code (str): Project code (prefix_00001) - required
        user_id (str): (prefix.username) - required
    """
    raise NotImplementedError('Not yet implemented.')
