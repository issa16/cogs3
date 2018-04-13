import random
import string
import uuid

from django.contrib.auth.models import Permission

from django.test import TestCase
from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from project.forms import ProjectCreationForm
from project.forms import ProjectUserMembershipCreationForm
from project.tests.test_models import ProjectCategoryTests
from project.tests.test_models import ProjectFundingSourceTests
from project.tests.test_models import ProjectTests
from project.tests.test_models import ProjectUserMembershipTests
from project.views import ProjectCreateView
from project.views import ProjectDetailView
from project.views import ProjectListView
from project.views import ProjectUserMembershipFormView
from project.views import ProjectUserMembershipListView
from project.views import ProjectUserRequestMembershipListView
from users.tests.test_models import CustomUserTests


class ProjectViewTests(TestCase):

    def setUp(self):
        # Create an institution
        base_domain = 'bangor.ac.uk'
        self.institution = InstitutionTests().create_institution(
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

        self.category = ProjectCategoryTests().create_project_category()
        self.funding_source = ProjectFundingSourceTests().create_project_funding_source()

    def access_view_as_unauthorisied_user(self, path):
        """
        Ensure an unauthorised user can not access a particular view.

        Args:
            path (str): Path to view.
        """
        headers = {
            'REMOTE_USER': 'invalid-remote-user',
            'eppn': 'invald-eppn',
        }
        response = self.client.get(path, **headers)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('register'))


class ProjectCreateViewTests(ProjectViewTests, TestCase):

    def test_project_create_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the project create view.
        """
        accounts = [
            {
                'username': self.student_username,
                'expected_status_code': 200,
            },
            {
                'username': self.techlead_username,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account.get('username'),
                'eppn': account.get('username'),
            }
            response = self.client.get(
                reverse('create-project'),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), ProjectCreationForm))
            self.assertTrue(isinstance(response.context_data.get('view'), ProjectCreateView))

    def test_project_create_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project create view.
        """
        self.access_view_as_unauthorisied_user(reverse('create-project'))


class ProjectListViewTests(ProjectViewTests, TestCase):

    def test_project_list_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the project list view.
        """
        accounts = [
            {
                'username': self.student_username,
                'expected_status_code': 200,
            },
            {
                'username': self.techlead_username,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account.get('username'),
                'eppn': account.get('username'),
            }
            response = self.client.get(
                reverse('project-application-list'),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('view'), ProjectListView))

    def test_project_list_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project list view.
        """
        self.access_view_as_unauthorisied_user(reverse('project-application-list'))


class ProjectDetailViewTests(ProjectViewTests, TestCase):

    def test_project_detail_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the details of projects they have created.
        """
        accounts = [
            {
                'user': self.student_user,
                'expected_status_code': 200,
            },
            {
                'user': self.techlead_user,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            # Create a project for the user
            project = ProjectTests().create_project(
                title='Project Title',
                code='scw-' + str(uuid.uuid4()),
                institution=self.institution,
                tech_lead=account.get('user'),
                category=self.category,
                funding_source=self.funding_source,
            )
            headers = {
                'REMOTE_USER': account.get('user').username,
                'eppn': account.get('user').username,
            }
            response = self.client.get(
                reverse('project-application-detail', args=[project.id]),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertEqual(response.context_data.get('project'), project)
            self.assertTrue(isinstance(response.context_data.get('view'), ProjectDetailView))

    def test_project_detail_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project detail view.
        """
        self.access_view_as_unauthorisied_user(reverse('project-application-detail', args=[1]))

    def test_project_detail_view_as_unauthorised_project_member(self):
        """
        Ensure only the project's technical lead user can view the details of the project.
        """
        # Create a project using the technical lead account.
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        project = ProjectTests().create_project(
            title='Project Title',
            code='scw-' + code,
            institution=self.institution,
            tech_lead=self.techlead_user,
            category=self.category,
            funding_source=self.funding_source,
        )
        # Attempt to access the project's detail view as a different user.
        headers = {
            'REMOTE_USER': self.student_username,
            'eppn': self.student_username,
        }
        response = self.client.get(
            reverse('project-application-detail', args=[project.id]),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('project-application-list'))


class ProjectUserMembershipFormViewTests(ProjectViewTests, TestCase):

    def test_project_user_membership_form_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the project user membership form.
        """
        accounts = [
            {
                'username': self.student_username,
                'expected_status_code': 200,
            },
            {
                'username': self.techlead_username,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account.get('username'),
                'eppn': account.get('username'),
            }
            response = self.client.get(
                reverse('project-membership-create'),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('form'), ProjectUserMembershipCreationForm))
            self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserMembershipFormView))

    def test_project_user_membership_form_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project user membership form.
        """
        self.access_view_as_unauthorisied_user(reverse('project-membership-create'))


class ProjectUserRequestMembershipListViewTests(ProjectViewTests, TestCase):

    def test_project_user_request_membership_list_view_as_an_authorised_user(self):
        """
        Ensure the correct accounts types can access the project user request membership list view.
        """
        accounts = [
            {
                'username': self.student_username,
                'expected_status_code': 302,
            },
            {
                'username': self.techlead_username,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account.get('username'),
                'eppn': account.get('username'),
            }
            response = self.client.get(
                reverse('project-user-membership-request-list'),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            if response.status_code == 200:
                self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserRequestMembershipListView))

    def test_project_user_request_membership_list_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project user request membership list view.
        """
        self.access_view_as_unauthorisied_user(reverse('project-user-membership-request-list'))


class ProjectUserMembershipListViewTests(ProjectViewTests, TestCase):

    def test_project_user_membership_list_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the project user membership list view.
        """
        accounts = [
            {
                'username': self.student_username,
                'expected_status_code': 200,
            },
            {
                'username': self.techlead_username,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'REMOTE_USER': account.get('username'),
                'eppn': account.get('username'),
            }
            response = self.client.get(
                reverse('project-membership-list'),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserMembershipListView))

    def test_project_user_membership_list_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project user membership list view.
        """
        self.access_view_as_unauthorisied_user(reverse('project-membership-list'))
