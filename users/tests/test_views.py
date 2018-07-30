from django.test import TestCase
from django.urls import reverse

from institution.models import Institution
from users.models import CustomUser
from users.models import Profile
from users.views import RegisterView


class UserViewTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        self.guest_user = CustomUser.objects.get(email='guest.user@external.ac.uk')


class RegisterViewTests(UserViewTests, TestCase):

    def test_register_user(self):
        """
        Ensure the register view is accessible for an authenticated shibboleth user.
        """
        email = '@'.join(['authorised-user', self.institution.base_domain])
        self.assertFalse(CustomUser.objects.filter(email=email).exists())
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'reason_for_account': 'HPC',
            'accepted_terms_and_conditions': True,
        }
        response = self.client.post(
            reverse('register'),
            data,
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(CustomUser.objects.filter(email=email).exists())
        user = CustomUser.objects.get(email=email)
        self.assertEqual(user.profile.account_status, Profile.AWAITING_APPROVAL)
        self.assertTrue(user.has_perm('project.add_project'))

    def test_register_view_as_unregistered_application_user(self):
        """
        Ensure the register view is accessible to an unregistred application user.
        """
        email = '@'.join(['unregistred-user', self.institution.base_domain])
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

    def test_register_view_as_authorised_application_user(self):
        """
        Ensure an authorised application user is redirected to the dashboard.
        """
        headers = {
            'Shib-Identity-Provider': self.shibboleth_user.profile.institution.identity_provider,
            'REMOTE_USER': self.shibboleth_user.email,
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
        Ensure an unauthorised user is redirected to the register view.
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
        Ensure an authorised user is redirected to the dashboard.
        """
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': self.shibboleth_user.email
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
        Ensure an authorised user is redirected to the logout view.
        """
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': self.shibboleth_user.email,
        }
        response = self.client.get(
            reverse('logout'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))
