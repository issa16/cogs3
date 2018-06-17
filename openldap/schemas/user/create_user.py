create_user_json = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$ref": "#/definitions/CreateUser",
    "definitions": {
        "CreateUser": {
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
            "title": "CreateUser"
        },
        "Data": {
            "type":
            "object",
            "additionalProperties":
            False,
            "properties": {
                "cn": {
                    "type": "string"
                },
                "sn": {
                    "type": "string"
                },
                "gidnumber": {
                    "type": "string"
                },
                "givenname": {
                    "type": "string"
                },
                "displayName": {
                    "type": "string"
                },
                "title": {
                    "type": "string"
                },
                "telephonenumber": {
                    "type": "string"
                },
                "homedirectory": {
                    "type": "string"
                },
                "loginshell": {
                    "type": "string"
                },
                "objectclass": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "mail": {
                    "type": "string"
                },
                "uid": {
                    "type": "string"
                },
                "uidnumber": {
                    "type": "string"
                }
            },
            "required": [
                "cn",
                "displayName",
                "gidnumber",
                "givenname",
                "homedirectory",
                "loginshell",
                "mail",
                "objectclass",
                "sn",
                "uid",
                "uidnumber",
            ],
            "title":
            "Data"
        }
    }
}
