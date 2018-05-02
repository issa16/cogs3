from django.test import TestCase
from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from users.tests.test_models import CustomUserTests


class DashboardViewTests(TestCase):

    def setUp(self):
        # Create an institution.
        self.base_domain = 'bangor.ac.uk'
        InstitutionTests.create_institution(
            name='Bangor University',
            base_domain=self.base_domain,
        )

    def test_empty_remote_user_header(self):
        """
        If the REMOTE_USER header is not present then the user should be redirected to the 
        login page.
        """
        headers = {'REMOTE_USER': None}
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')

    def test_as_authorised_shibboleth_user_and_unregistered_application_user(self):
        """
        If the REMOTE_USER and eppn header are present and the user is not a registered application
        user, then the user should be redirected to the account registration page.
        """
        headers = {
            'REMOTE_USER': 'unregistered-application-user@bangor.ac.uk',
            'eppn': 'unregistered-application-user@bangor.ac.uk',
        }
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))

    def test_as_authorised_shibboleth_user_and_registered_application_user(self):
        """
        If the REMOTE_USER and eppn header is present and the user is a registered application user,
        then the user should be redirected to the dashboard page and have the option to logout.
        """
        email = '@'.join(['user', self.base_domain])
        application_user = CustomUserTests.create_shibboleth_user(email=email)
        headers = {
            'REMOTE_USER': email,
            'eppn': email,
        }
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('project_user_requests_count'), 0)

        # Logout the user.
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))
