import random
import string
import uuid

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from institution.models import Institution
from project.forms import ProjectCreationForm
from project.forms import ProjectUserMembershipCreationForm
from project.models import Project
from project.models import ProjectCategory
from funding.models import FundingBody
from funding.models import FundingSource
from project.models import ProjectUserMembership
from project.views import ProjectCreateView
from project.views import ProjectDetailView
from project.views import ProjectListView
from project.views import ProjectUserMembershipFormView
from project.views import ProjectUserMembershipListView
from project.views import ProjectUserRequestMembershipListView
from users.models import CustomUser

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


class ProjectViewTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def setUp(self):
        # Load the user
        self.project_owner = CustomUser.objects.get(
            username="shibboleth.user@example.ac.uk"
        )

        self.project_applicant = CustomUser.objects.get(
            username="norman.gordon@example.ac.uk"
        )

        # Load the funding source
        self.funding_source = FundingSource.objects.filter(
            created_by=self.project_owner
        ).first()

    def _access_view_as_unauthorisied_application_user(self, url, expected_redirect_url):
        """
        Ensure an unauthorised application user can not access a url.

        Args:
            url (str): Url to view.
            expected_redirect_url (str): Expected redirect url.
        """
        headers = {
            'Shib-Identity-Provider': 'invald-identity-provider',
            'REMOTE_USER': 'invalid-remote-user',
        }
        response = self.client.get(
            url,
            **headers
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_redirect_url)


class ProjectCreateViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user_without_project_add_permission(self):
        """
        Ensure the project create view is not accessible to an authorised application user,
        who does not have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_applicant.profile.institution.identity_provider,
            'REMOTE_USER': self.project_applicant.email,
        }
        response = self.client.get(
            reverse('create-project'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_view_as_authorised_application_user_with_project_add_permission(self):
        """
        Ensure the project create view is accessible to an authorised application user,
        who does have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_owner.profile.institution.identity_provider,
            'REMOTE_USER': self.project_owner.email,
        }
        response = self.client.get(
            reverse('create-project'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data.get('form'), ProjectCreationForm))
        self.assertTrue(isinstance(response.context_data.get('view'), ProjectCreateView))

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project create view is not accessible to an unauthorised application user.
        """
        self._access_view_as_unauthorisied_application_user(
            reverse('create-project'),
            '/en-gb/accounts/login/?next=/en-gb/projects/create/',
        )


class ProjectListViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user_without_project_add_permission(self):
        """
        Ensure the project list view is not accessible to an authorised application user,
        who does not have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_applicant.profile.institution.identity_provider,
            'REMOTE_USER': self.project_applicant.email,
        }
        response = self.client.get(
            reverse('project-application-list'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_view_as_authorised_application_user_with_project_add_permission(self):
        """
        Ensure the project list view is accessible to an authorised application user,
        who does have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_owner.profile.institution.identity_provider,
            'REMOTE_USER': self.project_owner.email,
        }
        response = self.client.get(
            reverse('project-application-list'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data.get('view'), ProjectListView))

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project list view is not accessible to an unauthorised application user.
        """
        self._access_view_as_unauthorisied_application_user(
            reverse('project-application-list'),
            '/en-gb/accounts/login/?next=/en-gb/projects/applications/',
        )


class ProjectDetailViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user_without_project_add_permission(self):
        """
        Ensure the project detail view is not accessible to an authorised application user,
        who does not have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_applicant.profile.institution.identity_provider,
            'REMOTE_USER': self.project_applicant.email,
        }
        response = self.client.get(
            reverse('project-application-detail', args=[1]),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_view_as_authorised_application_user_with_project_add_permission(self):
        """
        Ensure the project detail view is accessible to an authorised application user,
        who does have the required permissions.
        """
        project = Project.objects.get(tech_lead=self.project_owner)
        headers = {
            'Shib-Identity-Provider': self.project_owner.profile.institution.identity_provider,
            'REMOTE_USER': self.project_owner.email,
        }
        response = self.client.get(
            reverse('project-application-detail', args=[project.id]),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('project'), project)
        self.assertTrue(isinstance(response.context_data.get('view'), ProjectDetailView))

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project detail view is not accessible to an unauthorised application user.
        """
        project = Project.objects.get(tech_lead=self.project_owner)
        self._access_view_as_unauthorisied_application_user(
            reverse('project-application-detail', args=[project.id]),
            '/en-gb/accounts/login/?next=/en-gb/projects/applications/1/',
        )


class ProjectUserMembershipFormViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user(self):
        """
        Ensure the project user membership form view is accessible to an authorised application user.
        """
        headers = {
            'Shib-Identity-Provider': self.project_applicant.profile.institution.identity_provider,
            'REMOTE_USER': self.project_applicant.email,
        }
        response = self.client.get(
            reverse('project-membership-create'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data.get('form'), ProjectUserMembershipCreationForm))
        self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserMembershipFormView))

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project user membership form view is not accessible to an unauthorised
        application user.
        """
        self._access_view_as_unauthorisied_application_user(
            reverse('project-membership-create'),
            '/en-gb/accounts/login/?next=/en-gb/projects/join/',
        )


class ProjectUserRequestMembershipListViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user_without_project_change_membership_permission(self):
        """
        Ensure the project user request membership list view is not accessible to an authorised
        application user, who does not have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_applicant.profile.institution.identity_provider,
            'REMOTE_USER': self.project_applicant.email,
        }
        response = self.client.get(
            reverse('project-user-membership-request-list'),
            **headers,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_view_as_authorised_application_user_with_project_change_membership_permission(self):
        """
        Ensure the project user request membership list view is accessible to an authorised
        application user, who does not have the required permissions.
        """
        headers = {
            'Shib-Identity-Provider': self.project_owner.profile.institution.identity_provider,
            'REMOTE_USER': self.project_owner.email,
        }
        response = self.client.get(
            reverse('project-user-membership-request-list'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserRequestMembershipListView))

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project user request membership list view is not accessible to an unauthorised
        application user.
        """
        self._access_view_as_unauthorisied_application_user(
            reverse('project-user-membership-request-list'),
            '/en-gb/accounts/login/?next=/en-gb/projects/memberships/user-requests/',
        )


class ProjectUserRequestMembershipUpdateViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user_without_project_change_membership_permission(self):
        """
        Ensure the project user request membership update view is not accessible to an authorised
        application user, who does not have the required permissions.
        """
        pass

    def test_view_as_authorised_application_user_with_project_change_membership_permission(self):
        """
        Ensure the project user request membership update view is accessible to an authorised
        application user, who does not have the required permissions.
        """
        pass

    def test_view_as_authorised_application_user_with_invalid_request_params(self):
        """
        Ensure it is not possible for a user, who is not the project's technical lead, to update
        a project membership user request.
        """
        pass

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project user request membership update view is not accessible to an unauthorised
        application user.
        """
        pass


class ProjectUserMembershipListViewTests(ProjectViewTests, TestCase):

    def test_view_as_authorised_application_user(self):
        """
        Ensure the project user membership list view is accessible to an unauthorised application
        user.
        """
        headers = {
            'Shib-Identity-Provider': self.project_owner.profile.institution.identity_provider,
            'REMOTE_USER': self.project_owner.email,
        }
        response = self.client.get(
            reverse('project-membership-list'),
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserMembershipListView))

    def test_view_as_unauthorised_application_user(self):
        """
        Ensure the project user membership list view is not accessible to an unauthorised
        application user.
        """
        self._access_view_as_unauthorisied_application_user(
            reverse('project-membership-list'),
            '/en-gb/accounts/login/?next=/en-gb/projects/memberships/',
        )
