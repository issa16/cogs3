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
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbG'
               'UuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk4O'
               'DY4LCJuYmYiOjE1MjcwOTgyNjgsImRhdGEiOnsiMCI6Inguam9lLmJsb2dncyIsImVycm9yIjoiIiwi'
               'Y291bnQiOjF9fQ.0Ah3-tL3sf_Nb1o7PkIvPlJ6P3q19_o7BK8Vbv_vGo4')
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
                "0": "x.joe.bloggs",
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
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGU'
               'uY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MTAwMTQ'
               'xLCJuYmYiOjE1MjcwOTk1NDEsImRhdGEiOnsiY24iOiJ4LmpvZS5ibG9nZ3MiLCJzbiI6IkJsb2dncyI'
               'sImdpZG51bWJlciI6IjUwMDAwMDEiLCJnaXZlbm5hbWUiOiJKb2UiLCJkaXNwbGF5TmFtZSI6Ik1yIEp'
               'vZSBCbG9nZ3MiLCJ0aXRsZSI6Ik1yIiwiaG9tZWRpcmVjdG9yeSI6Ii9ob21lL3guam9lLmJsb2dncyI'
               'sImxvZ2luc2hlbGwiOiIvYmluL2Jhc2giLCJvYmplY3RjbGFzcyI6WyJpbmV0T3JnUGVyc29uIiwicG9'
               'zaXhBY2NvdW50IiwidG9wIl0sInRlbGVwaG9uZW51bWJlciI6IjAwMDAwLTAwMC0wMDAiLCJtYWlsIjo'
               'iam9lLmJsb2dnc0BiYW5nb3IuYWMudWsiLCJ1aWQiOiJ4LmpvZS5ibG9nZ3MiLCJ1aWRudW1iZXIiOiI'
               '1MDAwMDAxIn19.QNKtIMjNc_zE6rSH-0MxxfFpWtE8TvaxWyliTW-J_rI')
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
                "cn": "x.joe.bloggs",
                "sn": "Bloggs",
                "gidnumber": "5000001",
                "givenname": "Joe",
                "displayName": "Mr Joe Bloggs",
                "title": "Mr",
                "homedirectory": "/home/x.joe.bloggs",
                "loginshell": "/bin/bash",
                "objectclass": [
                    "inetOrgPerson",
                    "posixAccount",
                    "top",
                ],
                "telephonenumber": "00000-000-000",
                "mail": "joe.bloggs@bangor.ac.uk",
                "uid": "x.joe.bloggs",
                "uidnumber": "5000001"
            }
        }
        result = user_api.create_user(user=self.user)
        self.assertEqual(result, expected_response)

        # Verify the user's profile information was updated correctly.
        self.assertEqual("5000001", self.user.profile.uid_number)
        self.assertEqual("x.joe.bloggs", self.user.profile.scw_username)

    @mock.patch('requests.get')
    def test_get_user_by_id_query(self, get_mock):
        """
        Get an existing user by id.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbG'
               'UuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk4O'
               'TIwLCJuYmYiOjE1MjcwOTgzMjAsImRhdGEiOnsiMCI6eyJ1aWQiOnsiMCI6Inguam9lLmJsb2dncyIs'
               'ImNvdW50IjoxfSwibWFpbCI6eyIwIjoiam9lLmJsb2dnc0BiYW5nb3IuYWMudWsiLCJjb3VudCI6MX0'
               'sImRpc3BsYXluYW1lIjp7IjAiOiJNciBKb2UgQmxvZ2dzIiwiY291bnQiOjF9LCJnaWROdW1iZXIiOn'
               'siMCI6Ijk5OTk5OTkiLCJjb3VudCI6MX0sInVpZG51bWJlciI6eyIwIjoiOTk5OTk5OSIsImNvdW50I'
               'joxfSwidGVsZXBob25lIjoiMDAwMDAtMDAwMDAwIn0sImVycm9yIjoiIiwiY291bnQiOjF9fQ.0pBYA'
               'IVhaRa_CPw3_40ViIIJTqHYq6L1hBAeS1QZdNc')
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
                        "0": "9999999",
                        "count": 1
                    },
                    "uidnumber": {
                        "0": "9999999",
                        "count": 1
                    },
                    "telephone": "00000-000000"
                },
                "error": "",
                "count": 1
            }
        }
        result = user_api.get_user_by_id(user_id='x.joe.bloggs')
        self.assertEqual(result, expected_response)

    @mock.patch('requests.get')
    def test_get_user_by_email_address_query(self, get_mock):
        """
        Get an existing user by email address.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbG'
               'UuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk4O'
               'TIwLCJuYmYiOjE1MjcwOTgzMjAsImRhdGEiOnsiMCI6eyJ1aWQiOnsiMCI6Inguam9lLmJsb2dncyIs'
               'ImNvdW50IjoxfSwibWFpbCI6eyIwIjoiam9lLmJsb2dnc0BiYW5nb3IuYWMudWsiLCJjb3VudCI6MX0'
               'sImRpc3BsYXluYW1lIjp7IjAiOiJNciBKb2UgQmxvZ2dzIiwiY291bnQiOjF9LCJnaWROdW1iZXIiOn'
               'siMCI6Ijk5OTk5OTkiLCJjb3VudCI6MX0sInVpZG51bWJlciI6eyIwIjoiOTk5OTk5OSIsImNvdW50I'
               'joxfSwidGVsZXBob25lIjoiMDAwMDAtMDAwMDAwIn0sImVycm9yIjoiIiwiY291bnQiOjF9fQ.0pBYA'
               'IVhaRa_CPw3_40ViIIJTqHYq6L1hBAeS1QZdNc')
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
                        "0": "9999999",
                        "count": 1
                    },
                    "uidnumber": {
                        "0": "9999999",
                        "count": 1
                    },
                    "telephone": "00000-000000"
                },
                "error": "",
                "count": 1
            }
        }
        result = user_api.get_user_by_email_address(email_address='joe.bloggs@bangor.ac.uk')
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
                "delete": "moved to cn=x.joe.bloggs,ou=Users,ou=Inactive,dc=example,dc=ac,dc=uk"
            }
        }
        result = user_api.deactivate_user_account(user=self.user)
        self.assertEqual(result, expected_response)

    @mock.patch('requests.post')
    def test_reset_user_password_query(self, post_mock):
        """
        Reset a user's password.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wb'
               'GUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MDk'
               '5MDU5LCJuYmYiOjE1MjcwOTg0NTksImRhdGEiOnsibWVzc2FnZSI6IlN1Y2Nlc3NmdWxseSByZXNld'
               'CB1c2VyIHBhc3N3b3JkLiJ9fQ.IoNA--5mFkCy_AtamPRZlP1YMUzzBI_PbHn7nJxEMyk')
        post_mock.return_value = self._mock_response(
            status=201,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1527099059,
            "nbf": 1527098459,
            "data": {
                "message": "Successfully reset user password."
            }
        }
        result = user_api.reset_user_password(user=self.user, password=12345678)
        self.assertEqual(result, expected_response)

    @mock.patch('requests.put')
    def test_activate_user_account_query(self, put_mock):
        """
        Activate an existing user's OpenLDAP account.
        """
        jwt = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wb'
               'GUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI3MTA'
               'wNTE0LCJuYmYiOjE1MjcwOTk5MTQsImRhdGEiOnsiZW5hYmxlIjoibW92ZWQgdG8gY249eC5qb2UuY'
               'mxvZ2dzLG91PUV4YW1wbGVVbml2ZXJzaXR5LG91PUluc3RpdHV0aW9ucyxvdT1Vc2VycyxkYz1leGF'
               'tcGxlLGRjPWFjLGRjPXVrIn19.w4JBxjvITyGPDRw2crT2S4ZwNyzGUFWL1JRhcLGdxA8')
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
                "moved to cn=x.joe.bloggs,ou=ExampleUniversity,ou=Institutions,ou=Users,dc=example,dc=ac,dc=uk"
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
                'user_id': 'x.joe.bloggs'
            }),
            (user_api.get_user_by_email_address, {
                'email_address': 'joe.bloggs@bangor.ac.uk'
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
