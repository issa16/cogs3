from django.conf import settings

from security.json_web_token import JSONWebToken


def decode_response(response):
    return JSONWebToken.decode(
        data=response.content.strip(),
        key=settings.OPENLDAP_JWT_KEY,
        audience=settings.OPENLDAP_JWT_AUDIENCE,
        algorithms=[settings.OPENLDAP_JWT_ALGORITHM],
    )


def verify_payload_data(payload, data, mapping):
    """
    Ensure data values match in both the payload and data dict's.
    """
    for payload_key, data_key in mapping.items():
        if payload[payload_key] != data[data_key]:
            message = 'Data Mismatch payload[{payload_key}] != data[{data_key}]'.format(
                payload_key=payload_key,
                data_key=data_key,
            )
            raise ValueError(message)


def raise_for_data_error(data):
    """
    Check for data errors.
    """
    if data.get('error', None):
        raise ValueError('Error Detected: {error}'.format(error=data['error']))
