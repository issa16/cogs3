from django.test import TestCase

from security.json_web_token import JSONWebToken


class JSONWebTokenTests(TestCase):

    def setUp(self):
        self.data = {
            "sub": "1234567890",
            "name": "John Doe",
            "iat": 1516239022,
        }
        self.key = '123456789'
        self.jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                    'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.'
                    'KTKkHQm6y79TfqMI0eUsIAFZMwfyYb_0LwIpQQqAQOQ')

    def test_json_web_token_encode(self):
        result = JSONWebToken.encode(data=self.data, key=self.key)
        self.assertEqual(result.decode(), self.jwt)

    def test_json_web_token_decode(self):
        result = JSONWebToken.decode(data=self.jwt, key=self.key)
        self.assertEqual(result, self.data)
