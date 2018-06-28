import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import user_api
from openldap.tests.test_api import OpenLDAPBaseAPITests
from users.tests.test_models import CustomUserTests


class OpenLDAPUserAPITests(OpenLDAPBaseAPITests):

    @mock.patch('requests.get')
    def test_list_users_query(self, get_mock):
        """
        Retrieve a list of all users.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGUu'
               'Y29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk4ODY4L'
               'CJuYmYiOjE1MjcwOTgyNjgsImRhdGEiOnsiMCI6ImUuam9lLmJsb2dncyIsImVycm9yIjoiIiwiY291bn'
               'QiOjF9fQ.36rdXQHItN-McM2SvtyWmyZgPdhJTerl1fDTH79QLB0')
        get_mock.return_value = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527098868,
            "nbf": 1527098268,
            "data": {
                "0": "e.joe.bloggs",
                "error": "",
                "count": 1
            }
        }
        result = user_api.list_users()
        self.assertEqual(result, expected_response)

    @mock.patch('requests.post')
    def test_create_user_query(self, post_mock):
        """
        Create a User.
        """
        jwt = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGUu'
               'Y29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MTAwMTQxL'
               'CJuYmYiOjE1MjcwOTk1NDEsImRhdGEiOnsiY24iOiJlLmpvZS5ibG9nZ3MiLCJzbiI6IkJsb2dncyIsIm'
               'dpZE51bWJlciI6IjUwMDAwMDEiLCJnaXZlbm5hbWUiOiJKb2UiLCJkaXNwbGF5TmFtZSI6Ik1yIEpvZSB'
               'CbG9nZ3MiLCJ0aXRsZSI6Ik1yIiwiaG9tZWRpcmVjdG9yeSI6Ii9ob21lL2Uuam9lLmJsb2dncyIsImxv'
               'Z2luc2hlbGwiOiIvYmluL2Jhc2giLCJvYmplY3RjbGFzcyI6WyJpbmV0T3JnUGVyc29uIiwicG9zaXhBY'
               '2NvdW50IiwidG9wIl0sInRlbGVwaG9uZW51bWJlciI6IjAwMDAwLTAwMC0wMDAiLCJtYWlsIjoic2hpYm'
               'JvbGV0aC51c2VyQGV4YW1wbGUuYWMudWsiLCJ1aWQiOiJlLmpvZS5ibG9nZ3MiLCJ1aWRudW1iZXIiOiI'
               '1MDAwMDAxIn19.-fgHQj_NkS97MQ2yAWACRPTdWOS00fMy8hSsQjj6JJM')
        post_mock.return_value = self._mock_response(
            status=201,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527100141,
            "nbf": 1527099541,
            "data": {
                "cn": "e.joe.bloggs",
                "sn": "Bloggs",
                "gidNumber": "5000001",
                "givenname": "Joe",
                "displayName": "Mr Joe Bloggs",
                "title": "Mr",
                "homedirectory": "/home/e.joe.bloggs",
                "loginshell": "/bin/bash",
                "objectclass": [
                    "inetOrgPerson",
                    "posixAccount",
                    "top",
                ],
                "telephonenumber": "00000-000-000",
                "mail": "shibboleth.user@example.ac.uk",
                "uid": "e.joe.bloggs",
                "uidnumber": "5000001"
            }
        }
        result = user_api.create_user(user=self.user)
        self.assertEqual(result, expected_response)

        # Verify the user's profile information was updated correctly.
        self.assertEqual("5000001", self.user.profile.uid_number)
        self.assertEqual("e.joe.bloggs", self.user.profile.scw_username)

    @mock.patch('requests.get')
    def test_get_user_by_id_query(self, get_mock):
        """
        Get an existing user by id.
        """
        jwt = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGUuY'
               '29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk4OTIwLCJ'
               'uYmYiOjE1MjcwOTgzMjAsImRhdGEiOnsiMCI6eyJ1aWQiOnsiMCI6ImUuam9lLmJsb2dncyIsImNvdW50I'
               'joxfSwibWFpbCI6eyIwIjoic2hpYmJvbGV0aC51c2VyQGV4YW1wbGUuYWMudWsiLCJjb3VudCI6MX0sImR'
               'pc3BsYXluYW1lIjp7IjAiOiJNciBKb2UgQmxvZ2dzIiwiY291bnQiOjF9LCJnaWROdW1iZXIiOnsiMCI6I'
               'jk5OTk5OTkiLCJjb3VudCI6MX0sInVpZG51bWJlciI6eyIwIjoiOTk5OTk5OSIsImNvdW50IjoxfSwidGV'
               'sZXBob25lIjoiMDAwMDAtMDAwLTAwMCJ9LCJlcnJvciI6IiIsImNvdW50IjoxfX0.sKa989E6cfZMTwHNL'
               'oGJTGpFx4KvC3fwQ6f-xVCImAg')
        get_mock.return_value = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527098920,
            "nbf": 1527098320,
            "data": {
                "0": {
                    "uid": {
                        "0": "e.joe.bloggs",
                        "count": 1
                    },
                    "mail": {
                        "0": "shibboleth.user@example.ac.uk",
                        "count": 1
                    },
                    "displayname": {
                        "0": "Mr Joe Bloggs",
                        "count": 1
                    },
                    "gidNumber": {
                        "0": "9999999",
                        "count": 1
                    },
                    "uidnumber": {
                        "0": "9999999",
                        "count": 1
                    },
                    "telephone": "00000-000-000"
                },
                "error": "",
                "count": 1
            }
        }
        result = user_api.get_user_by_id(user_id='e.joe.bloggs')
        self.assertEqual(result, expected_response)

    @mock.patch('requests.get')
    def test_get_user_by_email_address_query(self, get_mock):
        """
        Get an existing user by email address.
        """
        jwt = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGUu'
               'Y29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk4OTIwL'
               'CJuYmYiOjE1MjcwOTgzMjAsImRhdGEiOnsiMCI6eyJ1aWQiOnsiMCI6ImUuam9lLmJsb2dncyIsImNvdW'
               '50IjoxfSwibWFpbCI6eyIwIjoic2hpYmJvbGV0aC51c2VyQGV4YW1wbGUuYWMudWsiLCJjb3VudCI6MX0'
               'sImRpc3BsYXluYW1lIjp7IjAiOiJNciBKb2UgQmxvZ2dzIiwiY291bnQiOjF9LCJnaWROdW1iZXIiOnsi'
               'MCI6Ijk5OTk5OTkiLCJjb3VudCI6MX0sInVpZG51bWJlciI6eyIwIjoiOTk5OTk5OSIsImNvdW50Ijoxf'
               'SwidGVsZXBob25lIjoiMDAwMDAtMDAwLTAwMCJ9LCJlcnJvciI6IiIsImNvdW50IjoxfX0.sKa989E6cf'
               'ZMTwHNLoGJTGpFx4KvC3fwQ6f-xVCImAg')
        get_mock.return_value = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527098920,
            "nbf": 1527098320,
            "data": {
                "0": {
                    "uid": {
                        "0": "e.joe.bloggs",
                        "count": 1
                    },
                    "mail": {
                        "0": "shibboleth.user@example.ac.uk",
                        "count": 1
                    },
                    "displayname": {
                        "0": "Mr Joe Bloggs",
                        "count": 1
                    },
                    "gidNumber": {
                        "0": "9999999",
                        "count": 1
                    },
                    "uidnumber": {
                        "0": "9999999",
                        "count": 1
                    },
                    "telephone": "00000-000-000"
                },
                "error": "",
                "count": 1
            }
        }
        result = user_api.get_user_by_email_address(email_address='shibboleth.user@example.ac.uk')
        self.assertEqual(result, expected_response)

    @skip("Pending OpenLDAP fix")
    @mock.patch('requests.delete')
    def test_deactivate_user_account_query(self, delete_mock):
        """
        Deactivate an existing user's OpenDLAP account
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wb'
               'GUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MTA'
               'wNTk3LCJuYmYiOjE1MjcwOTk5OTcsImRhdGEiOnsiZGVsZXRlIjoibW92ZWQgdG8gY249eC5qb2UuY'
               'mxvZ2dzLG91PVVzZXJzLG91PUluYWN0aXZlLGRjPWV4YW1wbGUsZGM9YWMsZGM9dWsifX0.KIac7dO'
               'JHfhPGPFJrSkKAtd5bIIOKBQaO9_82rB1pkA')
        delete_mock.return_value = self._mock_response(
            status=204,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527100597,
            "nbf": 1527099997,
            "data": {
                "delete": "moved to cn=e.joe.bloggs,ou=Users,ou=Inactive,dc=example,dc=ac,dc=uk"
            }
        }
        result = user_api.deactivate_user_account(user=self.user)
        self.assertEqual(result, expected_response)

    @mock.patch('requests.post')
    def test_reset_user_password_query(self, post_mock):
        """
        Reset a user's password.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGU'
               'uY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI5MjQ5MjM'
               'zLCJuYmYiOjE1MjkyNDg2MzMsImRhdGEiOnsicGFzc3dvcmQiOiJTdWNjZXNzZnVsbHkgcmVzZXQgcGF'
               'zc3dvcmQifX0.ZC9yWYpDwszRs3TIt1naWmg0BSbl3U5SiW1LJ_hVEwM')
        post_mock.return_value = self._mock_response(
            status=201,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1529249233,
            "nbf": 1529248633,
            "data": {
                "password": "Successfully reset password"
            }
        }
        result = user_api.reset_user_password(user=self.user, password=12345678)
        self.assertEqual(result, expected_response)

    @mock.patch('requests.put')
    def test_activate_user_account_query(self, put_mock):
        """
        Activate an existing user's OpenLDAP account.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGUu'
               'Y29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MTAwNTE0L'
               'CJuYmYiOjE1MjcwOTk5MTQsImRhdGEiOnsiZW5hYmxlIjoibW92ZWQgdG8gY249ZS5qb2UuYmxvZ2dzLG'
               '91PUV4YW1wbGVVbml2ZXJzaXR5LG91PUluc3RpdHV0aW9ucyxvdT1Vc2VycyxkYz1leGFtcGxlLGRjPWF'
               'jLGRjPXVrIn19.VkuQvx8sF1FJ4JnBSemr6BVKFvmBBpI6QsW2_piLqZA')
        put_mock.return_value = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527100514,
            "nbf": 1527099914,
            "data": {
                "enable":
                "moved to cn=e.joe.bloggs,ou=ExampleUniversity,ou=Institutions,ou=Users,dc=example,dc=ac,dc=uk"
            }
        }
        result = user_api.activate_user_account(user=self.user)
        self.assertEqual(result, expected_response)

    def test_query_exceptions(self):
        """
        Ensure each query raises the correct error/exception.
        """
        queries = [
            (user_api.list_users, None),
            (user_api.create_user, {
                'user': self.user,
            }),
            (user_api.get_user_by_id, {
                'user_id': 'e.joe.bloggs'
            }),
            (user_api.get_user_by_email_address, {
                'email_address': 'shibboleth.user@example.ac.uk'
            }),
            (user_api.reset_user_password, {
                'user': self.user,
                'password': '1234567',
            }),
            #(user_api.deactivate_user_account, {
            #    'user': self.user,
            #}),
            (user_api.activate_user_account, {
                'user': self.user,
            }),
        ]
        for query, query_kwargs in queries:
            self._test_query_with_invalid_json_schema(query, query_kwargs)
            self._test_query_with_connection_error(query, query_kwargs)
            self._test_query_with_http_error(query, query_kwargs)
            self._test_query_with_timeout_error(query, query_kwargs)
