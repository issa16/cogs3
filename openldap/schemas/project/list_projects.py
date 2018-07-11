list_projects_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/ListProjects",
    "definitions": {
        "ListProjects": {
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
            "title": "ListProjects"
        },
        "Data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "0": {
                    "type": "string"
                },
                "1": {
                    "type": "string"
                },
                "error": {
                    "type": "string"
                },
                "count": {
                    "type": "integer"
                }
            },
            "required": [
                "count",
                "error",
            ],
            "title": "Data"
        }
    }
}
