from django.test import TestCase

from django.urls import reverse

from institution.models import Institution
from users.tests.test_models import CustomUserTests
from users.views import RegisterView


class UserViewTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')


class RegisterViewTests(UserViewTests, TestCase):

    def test_register_view_as_an_unauthorised_user(self):
        """
        Ensure an unauthorised user can access the register view.
        """
        email = '@'.join(['unauthorised-user', self.institution.base_domain])
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('register'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data['view'], RegisterView))

    def test_register_view_as_an_authorised_user(self):
        """
        Ensure an authorised user is redirected to the dashboard and can not access
        the register view.
        """
        email = '@'.join(['user', self.institution.base_domain])
        CustomUserTests.create_shibboleth_user(email=email)
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('register'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class LoginViewTests(UserViewTests, TestCase):

    def test_login_view_as_an_unauthorised_user(self):
        """
        Ensure an unauthorised user can access the register view.
        """
        email = '@'.join(['unauthorised-user', self.institution.base_domain])
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('login'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url, reverse('register'))

    def test_login_view_as_an_authorised_user(self):
        """
        Ensure an authorised user is redirected to the dashboard and can not access
        the register view.
        """
        email = '@'.join(['user', self.institution.base_domain])
        CustomUserTests.create_shibboleth_user(email=email)
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('login'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class LogoutViewTests(UserViewTests, TestCase):

    def test_logout_view_as_an_unauthorised_user(self):
        """
        Ensure an unauthorised user is redirected to the register view.
        """
        email = '@'.join(['unauthorised-user', self.institution.base_domain])
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('logout'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))

    def test_logout_view_as_an_authorised_user(self):
        """
        Ensure an authorised user can access the logout view.
        """
        email = '@'.join(['user', self.institution.base_domain])
        CustomUserTests.create_shibboleth_user(email=email)
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        response = self.client.get(
            reverse('logout'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))
