reset_user_password_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/ResetPassword",
    "definitions": {
        "ResetPassword": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "iss": {
                    "type": "string"
                },
                "aud": {
                    "type": "string"
                },
                "iat": {
                    "type": "integer"
                },
                "nbf": {
                    "type": "integer"
                },
                "data": {
                    "$ref": "#/definitions/Data"
                }
            },
            "required": [
                "aud",
                "data",
                "iat",
                "iss",
                "nbf",
            ],
            "title": "ResetPassword"
        },
        "Data": {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "password": {
                    "type": "string"
                }
            },
            "title": "Data"
        }
    }
}
