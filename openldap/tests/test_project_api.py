import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import project_api
from openldap.tests.test_api import OpenLDAPBaseAPITests


class OpenLDAPProjectAPITests(OpenLDAPBaseAPITests):

    @staticmethod
    def mock_create_project_response():
        """
        Mock the JWT response returned from the LDAP API when creating a
        project.
        """
        jwt = (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL29wZW5s'
            'ZGFwLmV4YW1wbGUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZ'
            'S5jb20vIiwiaWF0IjoxNTI3MTAwMTQxLCJuYmYiOjE1MjcwOTk1NDEsImRhdGEiOn'
            'siY24iOiJzY3cwMDAwIiwibWVtYmVyVWlkIjoiZS5zaGliYm9sZXRoLnVzZXIiLCJ'
            'kZXNjcmlwdGlvbiI6InRlc3Rfc3lzdGVtX2FsbG9jYXRpb25fcmVxdWVzdF9hcHBy'
            'b3ZhbCIsImdpZE51bWJlciI6IjUwMDAwMDEiLCJvYmplY3RDbGFzcyI6WyJpbmV0T'
            '3JnUGVyc29uIiwicG9zaXhBY2NvdW50IiwidG9wIl19fQ.U_xkdgeQFPnEMQOaDKC'
            'uquDsj1mXJZKV8jMj9maWvzE'
        )
        return OpenLDAPBaseAPITests.mock_response(
            status=201, content=jwt.encode()
        )

    @staticmethod
    def mock_deactivate_project_response():
        """
        Mock the JWT response returned from the LDAP API when de-activating a
        project.
        """
        return OpenLDAPBaseAPITests.mock_response(status=204, content='')

    @mock.patch('requests.get')
    def test_list_projects_query(self, get_mock):
        """
        List a list of all projects.
        """
        jwt = (
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbG'
            'UuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI5MDU3O'
            'DM4LCJuYmYiOjE1MjkwNTcyMzgsImRhdGEiOnsiMCI6IlNDVzAwMDEiLCIxIjoiU0NXMDAwMiIsImVy'
            'cm9yIjoiIiwiY291bnQiOjJ9fQ.h1cDddZWelKagic0qGx6MLFnTiwJnaw80e2jIwZlNVg'
        )
        get_mock.return_value = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1529057838,
            "nbf": 1529057238,
            "data": {
                "0": "SCW0001",
                "1": "SCW0002",
                "error": "",
                "count": 2
            }
        }
        result = project_api.list_projects()
        self.assertEqual(result, expected_response)

    @mock.patch('requests.get')
    def test_get_project_query(self, get_mock):
        """
        Get an existing OpenLDAP project.
        """
        jwt = (
            'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL29wZW5sZGFwLmV4YW1wbGUuY'
            '29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5jb20vIiwiaWF0IjoxNTI5MzM0Mjg4LCJ'
            'uYmYiOjE1MjkzMzM2ODgsImRhdGEiOnsiMCI6eyJjbiI6eyIwIjoiU0NXMTAwMCIsImNvdW50IjoxfSwib'
            'WVtYmVyIjp7IjAiOiJ4LmpvZS5ibG9nZ3MiLCJjb3VudCI6MX19LCJlcnJvciI6IiIsImNvdW50IjoxfX0'
            '.pnNQ0M0wPXWQuEhD8Futt2MmHUxxvowneJPAHatJ7Ec'
        )
        get_mock.return_value = self._mock_response(
            status=200,
            content=jwt.encode(),
        )
        expected_response = {
            "iss": settings.OPENLDAP_JWT_ISSUER,
            "aud": settings.OPENLDAP_JWT_AUDIENCE,
            "iat": 1529334288,
            "nbf": 1529333688,
            "data": {
                "0": {
                    "cn": {
                        "0": "SCW1000",
                        "count": 1
                    },
                    "member": {
                        "0": "x.joe.bloggs",
                        "count": 1
                    }
                },
                "error": "",
                "count": 1
            }
        }
        result = project_api.get_project('SCW1000')
        self.assertEqual(result, expected_response)

    @skip("Pending implementation")
    @mock.patch('requests.post')
    def test_create_project_query(self, post_mock):
        """
        Create an OpenLDAP Project.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.put')
    def test_activate_project_query(self, mock_get):
        """
        Activate an existing OpenLDAP project.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.delete')
    def test_deactivate_project_query(self, mock_get):
        """
        Deactivate an existing OpenLDAP project.
        """
        pass
