from django.test import TestCase
from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from users.tests.test_models import CustomUserTests


class DashboardViewTests(TestCase):

    def setUp(self):
        # Create an institution.
        base_domain = 'bangor.ac.uk'
        InstitutionTests.create_institution(
            name='Bangor University',
            base_domain=base_domain,
        )

        # Create a technical lead user account.
        self.techlead_username = 'scw_techlead@' + base_domain
        self.techlead_password = '123456'
        self.techlead_user = CustomUserTests.create_techlead_user(
            username=self.techlead_username,
            password=self.techlead_password,
        )

        # Create a student user account.
        self.student_username = 'scw_student@' + base_domain
        self.student_password = '789123'
        self.student_user = CustomUserTests.create_student_user(
            username=self.student_username,
            password=self.student_password,
        )

    def test_dashboard_view_as_an_unauthorised_shibboleth_user(self):
        """
        If the REMOTE_USER header is not present then the user should be redirected to the login page.
        """
        headers = {
            'REMOTE_USER': None,
        }
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')

    def test_dashboard_view_as_an_authorised_shibboleth_user_and_unregistered_application_user(self):
        """
        If the REMOTE_USER and eppn header is present and the user is not a registered application
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

    def test_dashboard_view_as_an_authorised_shibboleth_and_registered_technical_lead_user(self):
        """
        If the REMOTE_USER and eppn header is present and the user is a registered application user,
        then the user should be redirected to the dashboard page and have the option to logout.
        """
        headers = {
            'REMOTE_USER': self.techlead_username,
            'eppn': self.techlead_username,
        }
        # Ensure the dashboard is available.
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

    def test_dashboard_view_as_an_authorised_shibboleth_and_registered_student_user(self):
        """
        If the REMOTE_USER and eppn header is present and the user is a registered application user,
        then the user should be redirected to the dashboard page and have the option to logout.
        """
        headers = {
            'REMOTE_USER': self.student_username,
            'eppn': self.student_username,
        }
        # Ensure the dashboard is available.
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)

        # Logout the user.
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))