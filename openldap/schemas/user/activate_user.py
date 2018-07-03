activate_user_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/EnableAccount",
    "definitions": {
        "EnableAccount": {
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
            "title": "EnableAccount"
        },
        "Data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enable": {
                    "type": "string"
                }
            },
            "required": [
                "enable",
            ],
            "title": "Data"
        }
    }
}
