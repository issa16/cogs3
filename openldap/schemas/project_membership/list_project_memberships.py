list_project_memberships_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/ListProjectMemberships",
    "definitions": {
        "0": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "member": {
                    "$ref": "#/definitions/Member"
                }
            },
            "required": ["member"],
            "title": "0"
        },
        "ListProjectMemberships": {
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
            "title": "ListProjectMemberships"
        },
        "Data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "0": {
                    "$ref": "#/definitions/0"
                },
                "error": {
                    "type": "string"
                },
                "count": {
                    "type": "integer"
                }
            },
            "required": ["count", "error"],
            "title": "Data"
        },
        "Member": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "0": {
                    "type": "string"
                },
                "count": {
                    "type": "integer"
                }
            },
            "required": ["count"],
            "title": "Member"
        }
    }
}
