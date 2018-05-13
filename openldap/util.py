from django.conf import settings

from security.json_web_token import JSONWebToken


def decode_response(response):
    return JSONWebToken.decode(
        data=response.content,
        key=settings.OPENLDAP_JWT_KEY,
        audience=settings.OPENLDAP_JWT_AUDIENCE,
        algorithms=[settings.OPENLDAP_JWT_ALGORITHM],
    )
