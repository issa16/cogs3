from django.test import TestCase

from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from users.tests.test_models import CustomUserTests
from users.views import RegisterView


class UserViewTests(TestCase):

    def setUp(self):
        # Create an institution
        self.base_domain = 'bangor.ac.uk'
        InstitutionTests.create_institution(
            name='Bangor University',
            base_domain=self.base_domain,
        )


class RegisterViewTests(UserViewTests, TestCase):

    def test_register_view_as_an_unauthorised_user(self):
        """
        Ensure an unauthorised user can access the register view.
        """
        unauthorised_email = 'unauthorised-user@bangor.ac.uk'
        headers = {
            'REMOTE_USER': unauthorised_email,
            'eppn': unauthorised_email,
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
        user = CustomUserTests.create_shibboleth_user(email='@'.join(['user', self.base_domain]))
        headers = {
            'REMOTE_USER': user.username,
            'eppn': user.username,
        }
        response = self.client.get(
            reverse('register'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class LogoutViewTests(UserViewTests, TestCase):

    def test_logout_view_as_an_unauthorised_user(self):
        """
        Ensure an unauthorised user is redirected to the register view.
        """
        unauthorised_email = 'unauthorised-user@' + self.base_domain
        headers = {
            'REMOTE_USER': unauthorised_email,
            'eppn': unauthorised_email,
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
        user = CustomUserTests.create_shibboleth_user(email='@'.join(['user', self.base_domain]))
        headers = {
            'REMOTE_USER': user.email,
            'eppn': user.email,
        }
        response = self.client.get(
            reverse('logout'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))
