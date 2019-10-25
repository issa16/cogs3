import jsonschema
import mock
import requests

from django.conf import settings
from django.test import TestCase

from users.models import CustomUser


class OpenLDAPBaseAPITests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        settings.OPENLDAP_HOST = 'https://example.com/'
        settings.OPENLDAP_JWT_KEY = 'K2tAb8QC7eychxEr'
        settings.OPENLDAP_JWT_ISSUER = 'https://openldap.example.com/'
        settings.OPENLDAP_JWT_AUDIENCE = 'https://openldap.example.com/'
        settings.OPENLDAP_JWT_ALGORITHM = 'HS256'

        self.user = CustomUser.objects.get(
            email='shibboleth.user@example.ac.uk'
        )

    @staticmethod
    def mock_response(
        content=None, status=200, json_data=None, raise_for_status=None
    ):
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
    @mock.patch('requests.post')
    @mock.patch('requests.put')
    @mock.patch('requests.delete')
    def _test_query_with_invalid_json_schema(
        self, query, query_kwargs, delete_mock, put_mock, post_mock, get_mock
    ):
        """
        Ensure a ValidationError is raised if the decoded JWT does not conform to the required
        json schema.
        """
        jwt = (
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGU'
            'uY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIn0.0nWb_yS8s9nwxP4vC9E'
            '38xCuutmrqD8EJh-6SpXXmiU'
        )
        delete_mock.return_value = OpenLDAPBaseAPITests.mock_response(
            status=204, content=jwt.encode()
        )
        put_mock.return_value = OpenLDAPBaseAPITests.mock_response(
            status=200, content=jwt.encode()
        )
        post_mock.return_value = OpenLDAPBaseAPITests.mock_response(
            status=201, content=jwt.encode()
        )
        get_mock.return_value = OpenLDAPBaseAPITests.mock_response(
            status=200, content=jwt.encode()
        )
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            query(**query_kwargs) if query_kwargs else query()

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.put')
    @mock.patch('requests.delete')
    def _test_query_with_connection_error(
        self, query, query_kwargs, delete_mock, put_mock, post_mock, get_mock
    ):
        """
        Ensure a ConnectionError is raised if the request fails to connect.
        """
        mock_resp = OpenLDAPBaseAPITests.mock_response(
            status=504,
            raise_for_status=requests.exceptions.
            ConnectionError('ConnectionError.'),
        )
        delete_mock.return_value = mock_resp
        put_mock.return_value = mock_resp
        post_mock.return_value = mock_resp
        get_mock.return_value = mock_resp
        with self.assertRaises(requests.exceptions.ConnectionError):
            query(**query_kwargs) if query_kwargs else query()

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.put')
    @mock.patch('requests.delete')
    def _test_query_with_http_error(
        self, query, query_kwargs, delete_mock, put_mock, post_mock, get_mock
    ):
        """
        Ensure a HTTPError is raised if the the request returns a HTTP error status.
        """
        mock_resp = OpenLDAPBaseAPITests.mock_response(
            status=500,
            raise_for_status=requests.exceptions.
            HTTPError('Internal Server Error.'),
        )
        delete_mock.return_value = mock_resp
        put_mock.return_value = mock_resp
        post_mock.return_value = mock_resp
        get_mock.return_value = mock_resp
        with self.assertRaises(requests.exceptions.HTTPError):
            query(**query_kwargs) if query_kwargs else query()

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('requests.put')
    @mock.patch('requests.delete')
    def _test_query_with_timeout_error(
        self, query, query_kwargs, delete_mock, put_mock, post_mock, get_mock
    ):
        """
        Ensure a Timeout error is raised if the request times out.
        """
        mock_resp = OpenLDAPBaseAPITests.mock_response(
            status=504,
            raise_for_status=requests.exceptions.Timeout('Timeout'),
        )
        delete_mock.return_value = mock_resp
        put_mock.return_value = mock_resp
        post_mock.return_value = mock_resp
        get_mock.return_value = mock_resp
        with self.assertRaises(requests.exceptions.Timeout):
            query(**query_kwargs) if query_kwargs else query()
