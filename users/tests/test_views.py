from django.test import TestCase

from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from users.tests.test_models import CustomUserTests
from users.views import RegisterView


class UserViewTests(TestCase):

    def setUp(self):
        # Create an institution
        base_domain = 'bangor.ac.uk'
        self.institution = InstitutionTests.create_institution(
            name='Bangor University',
            base_domain=base_domain,
        )

        # Create a student user account
        self.student_user = CustomUserTests.create_student_user(
            username='scw_student@' + base_domain,
            password='654321',
        )


class RegisterViewTests(UserViewTests, TestCase):

    def test_register_view_as_unauthorised_user(self):
        """
        Ensure an unauthorised user can access the register view.
        """
        unauthorised_user_username = 'scw-user@bangor.ac.uk'
        headers = {
            'REMOTE_USER': unauthorised_user_username,
            'eppn': unauthorised_user_username,
        }
        response = self.client.get(
            reverse('register'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data['view'], RegisterView))

    def test_register_view_as_authorised_user(self):
        """
        Ensure an authorised user is redirected to the dashboard and can not access
        the register view.
        """
        headers = {
            'REMOTE_USER': self.student_user.username,
            'eppn': self.student_user.username,
        }
        response = self.client.get(
            reverse('register'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class LogoutViewTests(UserViewTests, TestCase):

    def test_logout_view_as_unauthorised_user(self):
        """
        Ensure an unauthorised user is redirected to the register view.
        """
        unauthorised_user_username = 'scw-user@bangor.ac.uk'
        headers = {
            'REMOTE_USER': unauthorised_user_username,
            'eppn': unauthorised_user_username,
        }
        response = self.client.get(
            reverse('logout'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))

    def test_logout_view_as_authorised_user(self):
        """
        Ensure an authorised user can access the logout view.
        """
        headers = {
            'REMOTE_USER': self.student_user.username,
            'eppn': self.student_user.username,
        }
        response = self.client.get(
            reverse('logout'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('logged_out'))
