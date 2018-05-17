import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import project_api
from openldap.tests.test_api import OpenLDAPBaseAPITests


class OpenLDAPProjectAPITests(OpenLDAPBaseAPITests):

    @skip("Pending implementation")
    @mock.patch('requests.get')
    def test_list_projects_query(self, mock_get):
        """
        List all projects.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.post')
    def test_create_project_query(self, mock_get):
        """
        Create a Project.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.put')
    def test_update_project_query(self, mock_get):
        """
        Update an existing project.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.delete')
    def test_delete_project_query(self, mock_get):
        """
        Delete a project.
        """
        pass
