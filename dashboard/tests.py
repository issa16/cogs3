from django.test import TestCase
from django.urls import reverse

from institution.tests import InstitutionTests
from users.tests import CustomUserTests


class DashboardViewTests(TestCase):

    def setUp(self):
        base_domain = 'bangor.ac.uk'
        InstitutionTests().create_institution(
            name='Bangor University',
            base_domain=base_domain,
        )

        self.techlead_username = 'scw_techlead@' + base_domain
        self.techlead_password = '123456'
        self.techlead_user = CustomUserTests().create_techlead_user(
            username=self.techlead_username,
            password=self.techlead_password,
        )

        self.student_username = 'scw_student@' + base_domain
        self.student_password = '789123'
        self.student_user = CustomUserTests().create_student_user(
            username=self.student_username,
            password=self.student_password,
        )

    def test_dashboard_access_as_an_unauthorised_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')

    def test_dashboard_access_as_an_authorised_techlead_user(self):
        login = self.client.login(username=self.techlead_username, password=self.techlead_password)
        self.assertTrue(login)

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('project_user_requests_count'), 0)

    def test_dashboard_access_as_an_authorised_student_user(self):
        login = self.client.login(username=self.student_username, password=self.student_password)
        self.assertTrue(login)

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context_data.get('project_user_requests_count'))
