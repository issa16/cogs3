import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import project_api
from openldap.tests.test_api import OpenLDAPBaseAPITests


class OpenLDAPProjectMembershipAPITests(OpenLDAPBaseAPITests):

    @staticmethod
    def mock_create_project_membership_response():
        """
        Mock the JWT response returned from the LDAP API when creating a
        project membership.
        """
        jwt = (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL29wZW5sZ'
            'GFwLmV4YW1wbGUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZXhhbXBsZS5'
            'jb20vIiwiaWF0IjoxNTI3MTAwMTQxLCJuYmYiOjE1MjcwOTk1NDEsImRhdGEiOnsiY'
            '291bnQiOjEsImVycm9yIjoiIiwicHJvamVjdCI6InNjdzAwMDAiLCJ1c2VyX2RuIjp'
            '7Im1lbWJlclVpZCI6ImUuc2hpYmJvbGV0aC51c2VyIn19fQ.Uy4ViGId1U0tB_tVEc'
            '8JgE44u4k1ibkxeNJQ3v7vpK0'
        )
        return OpenLDAPBaseAPITests.mock_response(
            status=201, content=jwt.encode()
        )

    @skip("Pending implementation")
    @mock.patch('requests.post')
    def test_create_project_membership_query(self, mock_get):
        """
        Create a project membership.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.put')
    def test_update_project_membership_query(self, mock_get):
        """
        Update an existing project membership.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.delete')
    def test_delete_project_membership_query(self, mock_get):
        """
        Delete a project membership.
        """
        pass
