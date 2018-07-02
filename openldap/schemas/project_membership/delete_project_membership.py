delete_project_membership_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/DeleteProjectMembership",
    "definitions": {
        "DeleteProjectMembership": {
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
            "title": "DeleteProjectMembership"
        },
        "Data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "error": {
                    "type": "string"
                },
                "count": {
                    "type": "integer"
                },
                "project": {
                    "type": "string"
                },
                "user_dn": {
                    "$ref": "#/definitions/UserDN"
                }
            },
            "required": [
                "count",
                "error",
                "project",
                "user_dn",
            ],
            "title": "Data"
        },
        "UserDN": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "memberUid": {
                    "type": "string"
                }
            },
            "required": ["memberUid"],
            "title": "UserDN"
        }
    }
}
