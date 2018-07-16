import random
import string
import uuid

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from institution.models import Institution
from project.forms import ProjectCreationForm
from project.forms import ProjectUserMembershipCreationForm
from project.tests.test_models import ProjectCategoryTests
from project.tests.test_models import ProjectTests
from project.tests.test_models import ProjectUserMembershipTests
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

        # Load the institution
        self.institution = Institution.objects.get(name="Example University")

        # Load the funding source
        self.funding_source = FundingSource.objects.filter(
            created_by=self.project_owner
        ).first()

    def _access_view_as_unauthorised_application_user(self, url, expected_redirect_url):
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
        self._access_view_as_unauthorised_application_user(
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
        self._access_view_as_unauthorised_application_user(
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
        self._access_view_as_unauthorised_application_user(
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
        self._access_view_as_unauthorised_application_user(
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
        self._access_view_as_unauthorised_application_user(
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

    def test_view_as_an_authorised_user(self):
        """
        Ensure the correct account types can access the project user membership list view.
        """
        accounts = [
            {
                'email': self.project_applicant.email,
                'expected_status_code': 200,
            },
            {
                'email': self.project_owner.email,
                'expected_status_code': 200,
            },
        ]
        for account in accounts:
            headers = {
                'Shib-Identity-Provider': self.institution.identity_provider,
                'REMOTE_USER': account.get('email'),
            }
            response = self.client.get(
                reverse('project-membership-list'),
                **headers,
            )
            self.assertEqual(response.status_code, account.get('expected_status_code'))
            self.assertTrue(isinstance(response.context_data.get('view'), ProjectUserMembershipListView))

    def test_view_as_an_unauthorised_user(self):
        """
        Ensure unauthorised users can not access the project user membership list view.
        """
        self._access_view_as_unauthorised_application_user(
            reverse('project-membership-list'),
            '/en-gb/accounts/login/?next=/en-gb/projects/memberships/'
        )


class ProjectUserRequestMembershipUpdateViewTests(ProjectViewTests, TestCase):

    def setUp(self):
        super().setUp()
        email = '@'.join(['norman.gordon',
            self.institution.base_domain])
        self.user = CustomUser.objects.get(email=email)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.project = Project.objects.get(tech_lead=self.project_owner)
        self.membership = ProjectUserMembership.objects.get(user=self.user)

    def post_status_change(self, email, status_in, status_set):
        ''' Sign in with email and post a status change from status_in
        to status_set
        '''
        # Set the starting status
        self.membership.status = status_in
        self.membership.save()
        self.membership.refresh_from_db()

        # Sign in as the user
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        self.client.get(reverse('login'), **headers)

        # Set up request data
        url = reverse('project-user-membership-update',kwargs={'pk': self.project.id})
        data = {
            'project_id': self.project.id,
            'request_id': self.membership.id,
        }
        data['status'] = status_set

        # Post the change
        self.client.post(url, data)
        self.client.get(reverse('logout'))

    def test_accept_invite(self):
        ''' Check that the user can accept or decline the invitation to join a
        project, but cannot revoke or suspend membership'''

        self.membership.initiated_by_user = False
        self.membership.save()

        cases = [
            [ProjectUserMembership.AWAITING_AUTHORISATION, ProjectUserMembership.AUTHORISED, True],
            [ProjectUserMembership.AWAITING_AUTHORISATION, ProjectUserMembership.DECLINED, True],
            [ProjectUserMembership.AUTHORISED, ProjectUserMembership.REVOKED, False],
            [ProjectUserMembership.AUTHORISED, ProjectUserMembership.SUSPENDED, False],
        ]
        for status_in, status_set, result in cases:
            self.post_status_change(self.user.email, status_in, status_set)
            self.membership.refresh_from_db()
            assert (self.membership.status == status_set) == result

    def test_change_invited_member_status(self):
        ''' Check that the tech cannot accept or decline the invite, but can
        revoke or suspend the membership once accepted'''

        self.membership.initiated_by_user = False
        self.membership.save()

        cases = [
            [ProjectUserMembership.AWAITING_AUTHORISATION, ProjectUserMembership.AUTHORISED, False],
            [ProjectUserMembership.AWAITING_AUTHORISATION, ProjectUserMembership.DECLINED, False],
            [ProjectUserMembership.AUTHORISED, ProjectUserMembership.REVOKED, True],
            [ProjectUserMembership.AUTHORISED, ProjectUserMembership.SUSPENDED, True],
        ]
        for status_in, status_set, result in cases:
            self.post_status_change(self.project_owner.email, status_in, status_set)
            self.membership.refresh_from_db()
            assert (self.membership.status == status_set) == result

    def test_change_member_requset_status(self):
        ''' Check that only the tech lead can change the
        change the status of a membership initiated by the tech lead '''

        self.membership.initiated_by_user = True
        self.membership.save()

        cases = [
            [ProjectUserMembership.AWAITING_AUTHORISATION, ProjectUserMembership.AUTHORISED],
            [ProjectUserMembership.AWAITING_AUTHORISATION, ProjectUserMembership.DECLINED],
            [ProjectUserMembership.AUTHORISED, ProjectUserMembership.REVOKED],
            [ProjectUserMembership.AUTHORISED, ProjectUserMembership.SUSPENDED],
        ]
        for status_in, status_set in cases:
            self.post_status_change(self.user.email, status_in, status_set)
            self.membership.refresh_from_db()
            assert self.membership.status == status_in

            self.post_status_change(self.project_owner.email, status_in, status_set)
            self.membership.refresh_from_db()
            assert self.membership.status == status_set

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
        self._access_view_as_unauthorised_application_user(
            reverse('project-membership-list'),
            '/en-gb/accounts/login/?next=/en-gb/projects/memberships/',
        )
