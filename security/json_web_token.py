import jwt


class JSONWebToken(object):

    @classmethod
    def encode(cls, data, key):
        return jwt.encode(data, key, algorithm='HS256')

    @classmethod
    def decode(cls, data, key, audience=None, algorithms=['HS256']):
        return jwt.decode(data, key, audience=audience, algorithms=algorithms)
