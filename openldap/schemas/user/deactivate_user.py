deactivate_user_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/DeleteUser",
    "definitions": {
        "DeleteUser": {
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
            "title": "DeleteUser"
        },
        "Data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "delete": {
                    "type": "string"
                }
            },
            "required": [
                "delete",
            ],
            "title": "Data"
        }
    }
}
