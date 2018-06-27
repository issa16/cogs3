from django.test import TestCase
from django.urls import reverse

from institution.models import Institution
from users.models import CustomUser


class DashboardViewTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.user = CustomUser.objects.get(email='joe.bloggs@example.ac.uk')

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
        self.assertEqual(response.url, '/en-gb/accounts/login/?next=/en-gb/')

    def test_view_as_an_authorised_shibboleth_user_and_an_unregistered_application_user(self):
        """
        If the required shibboleth headers are present and the user is not a registered application
        user, then the user should be redirected to the account registration page.
        """
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': 'unregistered-application-user@example.ac.uk',
        }
        response = self.client.get(
            reverse('home'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))

    def test_view_as_an_authorised_shibboleth_user_and_a_registered_application_user(self):
        """
        If the required shibboleth headers are present and the user is a registered application 
        user, then the user should be redirected to the dashboard page and have the option to logout.
        """
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': self.user.email,
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
