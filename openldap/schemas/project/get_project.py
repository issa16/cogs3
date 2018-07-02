get_project_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/GetProject",
    "definitions": {
        "0": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cn": {
                    "$ref": "#/definitions/CN"
                },
                "member": {
                    "$ref": "#/definitions/CN"
                }
            },
            "required": [
                "cn",
                "member",
            ],
            "title": "0"
        },
        "GetProject": {
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
            "title": "GetProject"
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
            "required": [
                "0",
                "count",
                "error",
            ],
            "title": "Data"
        },
        "CN": {
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
            "required": [
                "0",
                "count",
            ],
            "title": "CN"
        }
    }
}
