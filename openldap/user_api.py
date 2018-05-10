import json
import logging
import requests
import uuid

import jsonschema

from django.conf import settings

from openldap.schemas import list_users_schema
from security.json_web_token import JSONWebToken

logger = logging.getLogger('openldap')


def list_users():
    """
    List all users.
    """
    try:
        url = ''.join([settings.OPENLDAP_HOST, 'user/'])
        headers = {
            'Cache-Control': 'no-cache',
        }
        response = requests.get(
            url,
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        # Decode JWT
        response = JSONWebToken.decode(
            data=response.content,
            key=settings.OPENLDAP_JWT_KEY,
            audience=settings.OPENLDAP_JWT_AUDIENCE,
            algorithms=[settings.OPENLDAP_JWT_ALGORITHM],
        )
        # Validate json schema
        jsonschema.validate(response, list_users_schema)
        return response
    except jsonschema.exceptions.ValidationError:
        logger.exception('List all users :: Invalid json schema Exception')
        raise
    except requests.exceptions.ConnectionError:
        logger.exception('List all users :: ConnectionError Exception')
        raise
    except requests.exceptions.Timeout:
        logger.exception('List all users :: Timeout Exception')
        raise
    except requests.exceptions.HTTPError:
        logger.exception('List all users :: HTTPError Exception')
        raise
