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

get_user_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/GetUser",
    "definitions": {
        "0": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "uid": {
                    "$ref": "#/definitions/Displayname"
                },
                "mail": {
                    "$ref": "#/definitions/Displayname"
                },
                "displayname": {
                    "$ref": "#/definitions/Displayname"
                },
                "gidNumber": {
                    "$ref": "#/definitions/Displayname"
                },
                "uidnumber": {
                    "$ref": "#/definitions/Displayname"
                },
                "telephone": {
                    "type": "string"
                }
            },
            "required": ["displayname", "gidNumber", "mail", "telephone", "uid", "uidnumber"],
            "title": "0"
        },
        "GetUser": {
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
            "required": ["aud", "data", "iat", "iss", "nbf"],
            "title": "GetUser"
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
            "required": ["0", "count", "error"],
            "title": "Data"
        },
        "Displayname": {
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
            "required": ["0", "count"],
            "title": "Displayname"
        }
    }
}
