create_project_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/CreateProject",
    "definitions": {
        "CreateProject": {
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
            "title": "CreateProject"
        },
        "Data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "objectClass": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "gidNumber": {
                    "type": "string",
                    "format": "integer"
                },
                "cn": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                },
                "memberUid": {
                    "type": "string"
                }
            },
            "required": [
                "cn",
                "description",
                "gidNumber",
                "memberUid",
                "objectClass",
            ],
            "title": "Data"
        }
    }
}
