import jsonschema
import mock
import requests

from unittest import skip

from django.conf import settings
from django.test import TestCase

from openldap.api import project_api
from openldap.tests.test_api import OpenLDAPBaseAPITests


class OpenLDAPUserSystemAllocationAPITests(OpenLDAPBaseAPITests):

    @skip("Pending implementation")
    @mock.patch('requests.get')
    def test_get_system_allocation_query(self, mock_get):
        """
        Get a system allocation.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.put')
    def test_update_system_allocation_query(self, mock_get):
        """
        Update a system allocation.
        """
        pass

    @skip("Pending implementation")
    @mock.patch('requests.delete')
    def test_delete_system_allocation_query(self, mock_get):
        """
        Delete a system allocation.
        """
        pass
