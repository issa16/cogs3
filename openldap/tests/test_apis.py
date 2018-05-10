import jsonschema
import mock
import requests

from django.conf import settings
from django.test import TestCase

from openldap import user_api


class OpenLDAPUserAPITests(TestCase):

    def setUp(self):
        settings.OPENLDAP_HOST = 'https://example.com/'
        settings.OPENLDAP_JWT_KEY = 'K2tAb8QC7eychxEr'
        settings.OPENLDAP_JWT_ISSUER = 'https://openldap.example.com/'
        settings.OPENLDAP_JWT_AUDIENCE = 'https://openldap.example.com/'
        settings.OPENLDAP_JWT_ALGORITHM = 'HS256'

    def _mock_response(self, content=None, status=200, json_data=None, raise_for_status=None):
        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        mock_resp.content = content
        if json_data:
            mock_resp.json = mock.Mock(return_value=json_data)
        return mock_resp

    @mock.patch('requests.get')
    def test_list_users_query(self, mock_get):
        """
        Ensure a successful query to list all users returns correct and valid data.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4Y'
               'W1wbGUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0Ijo'
               'xNTI1OTUwODg1LCJuYmYiOjE1MjU5NTAyODUsImRhdGEiOnsiMCI6Inguam9lLmJsb2dncyIsI'
               'mVycm9yIjoiIiwiY291bnQiOjF9fQ.ZVHI-mnX_eCtuMRpoM137CMSuNIyHxuhY1TX_HKU1Sg')
        mock_resp = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        mock_get.return_value = mock_resp
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1525950885,
            "nbf": 1525950285,
            "data": {
                "0": "x.joe.bloggs",
                "error": "",
                "count": 1
            }
        }
        result = user_api.list_users()
        self.assertEqual(result, expected_response)

    @mock.patch('requests.get')
    def test_list_users_query_with_invalid_json_schema(self, mock_get):
        """
        Ensure a ValidationError is raised if the decoded JWT does not conform to the required 
        json schema.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW'
               '1wbGUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiZGF0YSI6ey'
               'IwIjoieC5qb2UuYmxvZ2dzIiwiZXJyb3IiOiIifX0.3YYk7ZwaJ5zfp_dgpRhy2X9oog_1cZDS4x'
               '1NC9fmvxk')
        mock_resp = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        mock_get.return_value = mock_resp

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            user_api.list_users()

    @mock.patch('requests.get')
    def test_list_users_query_with_connection_error(self, mock_get):
        """
        Ensure a ConnectionError is raised if the request fails to connect.
        """
        mock_resp = self._mock_response(
            status=504,
            raise_for_status=requests.exceptions.ConnectionError,
        )
        mock_get.return_value = mock_resp

        with self.assertRaises(requests.exceptions.ConnectionError):
            user_api.list_users()

    @mock.patch('requests.get')
    def test_list_users_query_with_timeout_error(self, mock_get):
        """
        Ensure a Timeout error is raised if the request to the list all users times out.
        """
        mock_resp = self._mock_response(
            status=504,
            raise_for_status=requests.exceptions.Timeout,
        )
        mock_get.return_value = mock_resp

        with self.assertRaises(requests.exceptions.Timeout):
            user_api.list_users()

    @mock.patch('requests.get')
    def test_list_users_query_with_http_error(self, mock_get):
        """
        Ensure a HTTPError is raised if the the request returns a HTTP error response status.
        """
        mock_resp = self._mock_response(
            status=500,
            raise_for_status=requests.exceptions.HTTPError("Internal Server Error."),
        )
        mock_get.return_value = mock_resp

        with self.assertRaises(requests.exceptions.HTTPError):
            user_api.list_users()
