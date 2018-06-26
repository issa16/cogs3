import jsonschema
import requests

from django.conf import settings
from django_rq import job


@job
def get_system_allocation(email):
    """
    Get a system allocation.

    Args:
        email (str): User's email address - required
    """
    raise NotImplementedError('Not yet implemented.')


@job
def update_system_allocation(email, system_id):
    """
    Update a system allocation.

    Args:
        email (str): User's email address - required
        system_id (str): System name [hawk, sunbird].
    """
    raise NotImplementedError('Not yet implemented.')


@job
def delete_system_allocation(email, system_id):
    """
    Delete a system allocation.

    Args:
        email (str): User's email address - required
        system_id (str): System name [hawk, sunbird].
    """
    raise NotImplementedError('Not yet implemented.')
