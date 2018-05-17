import jsonschema
import mock
import requests

from django.conf import settings
from django.test import TestCase


class OpenLDAPBaseAPITests(TestCase):

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
    def _test_query_with_invalid_json_schema(self, mock_get, query, query_args):
        """
        Ensure a ValidationError is raised if the decoded JWT does not conform to the required
        json schema.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGU'
               'uY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIn0.0nWb_yS8s9nwxP4vC9E'
               '38xCuutmrqD8EJh-6SpXXmiU')
        mock_resp = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        mock_get.return_value = mock_resp
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            query(query_args) if query_args else query()

    @mock.patch('requests.get')
    def _test_query_with_connection_error(self, mock_get, query, query_args):
        """
        Ensure a ConnectionError is raised if the request fails to connect.
        """
        mock_resp = self._mock_response(
            status=504,
            raise_for_status=requests.exceptions.ConnectionError('ConnectionError.'),
        )
        mock_get.return_value = mock_resp
        with self.assertRaises(requests.exceptions.ConnectionError):
            query(query_args) if query_args else query()

    @mock.patch('requests.get')
    def _test_query_with_http_error(self, mock_get, query, query_args):
        """
        Ensure a HTTPError is raised if the the request returns a HTTP error status.
        """
        mock_resp = self._mock_response(
            status=500,
            raise_for_status=requests.exceptions.HTTPError('Internal Server Error.'),
        )
        mock_get.return_value = mock_resp
        with self.assertRaises(requests.exceptions.HTTPError):
            query(query_args) if query_args else query()

    @mock.patch('requests.get')
    def _test_query_with_timeout_error(self, mock_get, query, query_args):
        """
        Ensure a Timeout error is raised if the request times out.
        """
        mock_resp = self._mock_response(
            status=504,
            raise_for_status=requests.exceptions.Timeout('Timeout'),
        )
        mock_get.return_value = mock_resp
        with self.assertRaises(requests.exceptions.Timeout):
            query(query_args) if query_args else query()
