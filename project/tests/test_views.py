from django.test import TestCase
from django.urls import reverse

from institution.tests import InstitutionTests
from users.tests.test_models import CustomUserTests


class ProjectViewTests(TestCase):

    def setUp(self):
        # Create an institution
        base_domain = 'bangor.ac.uk'
        InstitutionTests().create_institution(
            name='Bangor University',
            base_domain=base_domain,
        )

        # Create a technical lead user account
        self.techlead_username = 'scw_techlead@' + base_domain
        self.techlead_password = '123456'
        self.techlead_user = CustomUserTests().create_techlead_user(
            username=self.techlead_username,
            password=self.techlead_password,
        )

        # Create a student user account
        self.student_username = 'scw_student@' + base_domain
        self.student_password = '654321'
        self.student_user = CustomUserTests().create_student_user(
            username=self.student_username,
            password=self.student_password,
        )


class ProjectListViewTests(ProjectViewTests, TestCase):

    def test_project_list_view_as_an_authorised_user(self):
        """
        Ensure both student and technical lead accounts can access the project list view.
        """
        accounts = [
            self.student_username,
            self.techlead_username,
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account,
                'eppn': account,
            }
            response = self.client.get(reverse('project-application-list'), **headers)
            self.assertEqual(response.status_code, 200)


class ProjectCreateViewTests(ProjectViewTests, TestCase):

    def test_project_create_view_as_an_authorised_user(self):
        """
        Ensure both student and technical lead accounts can access the create a project view.
        """
        accounts = [
            self.student_username,
            self.techlead_username,
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account,
                'eppn': account,
            }
            response = self.client.get(reverse('create-project'), **headers)
            self.assertEqual(response.status_code, 200)
