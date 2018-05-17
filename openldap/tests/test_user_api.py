import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import user_api
from openldap.tests.test_api import OpenLDAPBaseAPITests


class OpenLDAPUserAPITests(OpenLDAPBaseAPITests):

    @mock.patch('requests.get')
    def test_list_users_query(self, mock_get):
        """
        Retrieve a list of all users.
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

    @skip("Pending implementation")
    @mock.patch('requests.post')
    def test_create_user_query(self, mock_get):
        """
        Create a User.
        """
        pass

    @mock.patch('requests.get')
    def test_get_user_by_id_query(self, mock_get):
        """
        Retrieve a user via their user id.
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
    def test_get_user_by_email_address_query(self, mock_get):
        """
        Retrieve a user via their email address.
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

    @skip("Pending implementation")
    @mock.patch('requests.delete')
    def test_delete_user_query(self, mock_get):
        """
        Delete (deactivated) a user via the user's email address.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.post')
    def test_reset_user_password_query(self, mock_get):
        """
        Reset a user's password.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.put')
    def test_enable_user_account_query(self, mock_get):
        """
        Enable a user's account.
        """
        pass

    def test_query_exceptions(self):
        """
        Ensure each query raises the correct error/exception.
        """
        queries = [
            (user_api.list_users, None),
            #(user_api.test_create_user, None),
            (user_api.get_user_by_id, 'x.joe.bloggs'),
            (user_api.test_get_user_by_email_address, 'joe.bloggs@bangor.ac.uk'),
            #(user_api.test_delete_user, 'joe.bloggs@bangor.ac.uk'),
            #(user_api.test_reset_user_password, 'joe.bloggs@bangor.ac.uk'),
            #(user_api.test_enable_user_account, 'joe.bloggs@bangor.ac.uk'),
        ]
        for query, args in queries:
            self._test_query_with_invalid_json_schema(query=query, query_args=args)
            self._test_query_with_connection_error(query=query, query_args=args)
            self._test_query_with_http_error(query=query, query_args=args)
            self._test_query_with_timeout_error(query=query, query_args=args)
