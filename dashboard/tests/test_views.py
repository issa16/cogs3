from django.test import TestCase
from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from users.tests.test_models import CustomUserTests


class DashboardViewTests(TestCase):

    def setUp(self):
        # Create an institution.
        self.institution = InstitutionTests.create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
            identity_provider='https://idp.bangor.ac.uk/shibboleth',
        )

    def test_view_without_required_headers(self):
        """
        If the required headers are not present then the user should be redirected to the login page.
        """
        headers = {}
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')

    def test_view_as_an_authorised_shibboleth_user_and_an_unregistered_application_user(self):
        """
        If the required headers are present and the user is not a registered application
        user, then the user should be redirected to the account registration page.
        """
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': 'unregistered-application-user@bangor.ac.uk',
        }
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))

    def test_view_as_an_authorised_shibboleth_user_and_a_registered_application_user(self):
        """
        If the required headers are present and the user is a registered application user,
        then the user should be redirected to the dashboard page and have the option to logout.
        """
        email = '@'.join(['user', self.institution.base_domain])
        CustomUserTests.create_shibboleth_user(email=email)
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)

        # Logout the user.
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))
