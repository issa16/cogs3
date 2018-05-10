list_users_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/ListUsers",
    "definitions": {
        "ListUsers": {
            "type": "object",
            "additionalProperties": True,
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
            "required": ["aud", "data", "iat", "iss", "nbf"],
            "title": "ListUsers"
        },
        "Data": {
            "type": "object",
            "additionalProperties": True,
            "properties": {
                "error": {
                    "type": "string"
                },
                "count": {
                    "type": "integer"
                }
            },
            "required": ["count", "error"],
            "title": "Data"
        }
    }
}
