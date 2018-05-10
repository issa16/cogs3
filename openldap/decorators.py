import functools
import jsonschema
import requests


def OpenLDAPException(logger):

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except jsonschema.exceptions.ValidationError:
                logger.exception('Invalid json schema Exception')
                raise
            except requests.exceptions.ConnectionError:
                logger.exception('ConnectionError Exception')
                raise
            except requests.exceptions.Timeout:
                logger.exception('Timeout Exception')
                raise
            except requests.exceptions.HTTPError:
                logger.exception('HTTPError Exception')
                raise

        return wrapper

    return decorator
