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
    def test_get_user_by_id(self, mock_get):
        """
        Ensure the retrieval of a user via user id returns correct and valid data.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4Y'
               'W1wbGUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0Ijo'
               'xNTI1OTY2MzU5LCJuYmYiOjE1MjU5NjU3NTksImRhdGEiOnsiMCI6eyJ1aWQiOnsiMCI6Ingua'
               'm9lLmJsb2dncyIsImNvdW50IjoxfSwibWFpbCI6eyIwIjoiam9lLmJsb2dnc0BiYW5nb3IuYWM'
               'udWsiLCJjb3VudCI6MX0sImRpc3BsYXluYW1lIjp7IjAiOiJNciBKb2UgQmxvZ2dzIiwiY291b'
               'nQiOjF9LCJnaWROdW1iZXIiOnsiMCI6IjUwMDAwMDEiLCJjb3VudCI6MX0sInVpZG51bWJlciI'
               '6eyIwIjoiNTAwMDAwMSIsImNvdW50IjoxfSwidGVsZXBob25lIjoiMDAwMDAtMDAwMDAwIn0sI'
               'mVycm9yIjoiIiwiY291bnQiOjF9fQ.by9IPjLOms62uq91DswhGP0zi2wn2s4JvbD74xbPbxE')
        mock_resp = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        mock_get.return_value = mock_resp
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1525966359,
            "nbf": 1525965759,
            "data": {
                "0": {
                    "uid": {
                        "0": "x.joe.bloggs",
                        "count": 1
                    },
                    "mail": {
                        "0": "joe.bloggs@bangor.ac.uk",
                        "count": 1
                    },
                    "displayname": {
                        "0": "Mr Joe Bloggs",
                        "count": 1
                    },
                    "gidNumber": {
                        "0": "5000001",
                        "count": 1
                    },
                    "uidnumber": {
                        "0": "5000001",
                        "count": 1
                    },
                    "telephone": "00000-000000"
                },
                "error": "",
                "count": 1
            }
        }
        result = user_api.get_user_by_id('x.joe.bloggs')
        self.assertEqual(result, expected_response)

    @mock.patch('requests.get')
    def test_get_user_by_email_address(self, mock_get):
        """
        Ensure the retrieval of a user via email address returns correct and valid data.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbG'
               'UuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI1OTY3M'
               'zcyLCJuYmYiOjE1MjU5NjY3NzIsImRhdGEiOnsiMCI6eyJ1aWQiOnsiMCI6Inguam9lLmJsb2dncyIs'
               'ImNvdW50IjoxfSwibWFpbCI6eyIwIjoiam9lLmJsb2dnc0BiYW5nb3IuYWMudWsiLCJjb3VudCI6MX0'
               'sImRpc3BsYXluYW1lIjp7IjAiOiJNciBKb2UgQmxvZ2dzIiwiY291bnQiOjF9LCJnaWROdW1iZXIiOn'
               'siMCI6IjUwMDAwMDEiLCJjb3VudCI6MX0sInVpZG51bWJlciI6eyIwIjoiNTAwMDAwMSIsImNvdW50I'
               'joxfSwidGVsZXBob25lIjoiMDAwMDAtMDAwMDAwIn0sImVycm9yIjoiIiwiY291bnQiOjF9fQ.-yFhW'
               '3T_BVp3ON4N7jcz43LSvRmNOhqoZ64ZSqSulxg')
        mock_resp = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        mock_get.return_value = mock_resp
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1525967372,
            "nbf": 1525966772,
            "data": {
                "0": {
                    "uid": {
                        "0": "x.joe.bloggs",
                        "count": 1
                    },
                    "mail": {
                        "0": "joe.bloggs@bangor.ac.uk",
                        "count": 1
                    },
                    "displayname": {
                        "0": "Mr Joe Bloggs",
                        "count": 1
                    },
                    "gidNumber": {
                        "0": "5000001",
                        "count": 1
                    },
                    "uidnumber": {
                        "0": "5000001",
                        "count": 1
                    },
                    "telephone": "00000-000000"
                },
                "error": "",
                "count": 1
            }
        }
        result = user_api.test_get_user_by_email_address('joe.bloggs@bangor.ac.uk')
        self.assertEqual(result, expected_response)

    def test_query_exceptions(self):
        """
        Ensure each query raises the correct error/exception.
        """
        queries = [
            (user_api.list_users, None),
            (user_api.get_user_by_id, 'x.joe.bloggs'),
            (user_api.test_get_user_by_email_address, 'joe.bloggs@bangor.ac.uk'),
        ]
        for query, args in queries:
            self._test_query_with_invalid_json_schema(query=query, query_args=args)
            self._test_query_with_connection_error(query=query, query_args=args)
            self._test_query_with_http_error(query=query, query_args=args)
            self._test_query_with_timeout_error(query=query, query_args=args)

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
