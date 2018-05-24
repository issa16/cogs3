import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import project_api
from openldap.tests.test_api import OpenLDAPBaseAPITests


class OpenLDAPProjectMembershipAPITests(OpenLDAPBaseAPITests):

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
