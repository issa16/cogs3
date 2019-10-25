import datetime
import random
import string

import mock
from django.conf import settings
from django.core import mail
from django.test import TestCase

from institution.models import Institution
from openldap.tests.test_api import OpenLDAPBaseAPITests
from openldap.tests.test_project_api import OpenLDAPProjectAPITests
from openldap.tests.test_project_membership_api import \
    OpenLDAPProjectMembershipAPITests
from project.forms import (
    ProjectCreationForm, ProjectManageAttributionForm,
    ProjectSupervisorApproveForm, ProjectUserInviteForm,
    ProjectUserMembershipCreationForm, RSEAllocationRequestCreationForm,
    SystemAllocationRequestAdminForm, SystemAllocationRequestCreationForm
)
from project.models import (
    Project, ProjectUserMembership, SystemAllocationRequest
)
from users.models import CustomUser
from users.tests.test_models import CustomUserTests


class SystemAllocationRequestAdminFormTests(TestCase):
    """
    Ensure the System Allocation Request Admin form works correctly.
    """

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def setUp(self):
        self.project = Project.objects.get(code='scw0000')
        self.tech_lead = self.project.tech_lead

        mail.outbox = []  # Clear mail outbox

    # yapf: disable
    @mock.patch(
        'requests.post',
        side_effect=[
            OpenLDAPProjectAPITests.mock_create_project_response(),
            OpenLDAPProjectMembershipAPITests.mock_create_project_membership_response()
        ]
    )
    # yapf: enable
    def test_system_allocation_request_activation(self, post_mock):
        """
        Ensure the correct LDAP API url is called and email notification is 
        issued when approving a system allocation request.
        """
        form = SystemAllocationRequestAdminForm(
            data={
                'information': 'A test allocation',
                'start_date': '01/09/1985',
                'end_date': '01/09/1985',
                'allocation_cputime': '99999',
                'allocation_memory': '99999',
                'allocation_storage_home': '99999',
                'allocation_storage_scratch': '99999',
                'requirements_software': 'N/A',
                'requirements_training': 'N/A',
                'requirements_onboarding': 'N/A',
                'document': None,
                'attributions': [],
                'project': self.project.id,
                'status': SystemAllocationRequest.AWAITING_APPROVAL
            }
        )
        self.assertTrue(form.is_valid())

        # Approve the system allocation request and trigger LDAP API calls
        form.instance.status = SystemAllocationRequest.APPROVED
        form.save()

        # Ensure the args passed to LDAP to create a project are correct
        call_args, call_kwargs = post_mock.call_args_list[0]
        call_url = call_args[0]
        expected_call_url = f'{settings.OPENLDAP_HOST}project/'
        self.assertEqual(call_url, expected_call_url)
        # yapf: disable
        expected_call_kwargs = {
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            },
            'data': {
                'code': 'scw0000',
                'category': 1,
                'title': 'Project title (Project Leader = John Doe, Technical Lead = shibboleth.user@example.ac.uk)',
                'technical_lead': 'e.shibboleth.user'
            },
            'timeout': 5
        }
        # yapf: enable
        self.assertEqual(call_kwargs, expected_call_kwargs)

        # Ensure the args passed to LDAP to create a project membership are correct
        call_args, call_kwargs = post_mock.call_args_list[1]
        call_url = call_args[0]
        expected_call_url = f'{settings.OPENLDAP_HOST}project/member/scw0000/'
        self.assertEqual(call_url, expected_call_url)
        # yapf: disable
        expected_call_kwargs = {
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            },
            'data': {
                'email': 'shibboleth.user@example.ac.uk'
            },
            'timeout': 5
        }
        # yapf: enable
        self.assertEqual(call_kwargs, expected_call_kwargs)

        self.assertEqual(len(mail.outbox), 2)

        # Ensure system allocation email notification is correct
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.tech_lead.email])
        self.assertNotEqual(email.subject.find('Project scw0000 Created'), -1)
        self.assertNotEqual(email.body.find('scw0000 has been approved'), -1)
        self.assertNotEqual(email.body.find(self.tech_lead.first_name), -1)

        # Ensure project user membership email notification is correct
        email = mail.outbox[1]
        self.assertEqual(email.to, [self.tech_lead.email])
        self.assertNotEqual(
            email.subject.find('Project Membership Created'), -1
        )
        self.assertNotEqual(
            email.body.find('Project scw0000 Membership Update'), -1
        )
        self.assertNotEqual(email.body.find(self.tech_lead.first_name), -1)

    # yapf: disable
    @mock.patch(
        'requests.delete',
        side_effect=[OpenLDAPProjectAPITests.mock_deactivate_project_response()]
    )
    # yapf: enable
    def test_system_allocation_request_ldap_deactivation(self, delete_mock):
        """
        Ensure the correct LDAP API url is called and email notification is 
        issued when de-activating a system allocation request.
        """
        system_allocation_request = SystemAllocationRequest(
            project=self.project,
            start_date='2019-07-30',
            end_date='2019-09-30',
            status=SystemAllocationRequest.APPROVED
        )
        system_allocation_request.save()

        form = SystemAllocationRequestAdminForm(
            data={
                'project': self.project.id,
                'start_date': '2019-07-30',
                'end_date': '2019-09-30',
                'status': SystemAllocationRequest.SUSPENDED
            },
            instance=system_allocation_request
        )
        self.assertTrue(form.is_valid())

        # Suspend system allocation request and trigger LDAP API calls
        form.save()

        # Ensure args passed to LDAP to deactivate a project are correct
        call_args, call_kwargs = delete_mock.call_args_list[0]
        call_url = call_args[0]
        expected_call_url = f'{settings.OPENLDAP_HOST}project/scw0000/'
        self.assertEqual(call_url, expected_call_url)
        # yapf: disable
        expected_call_kwargs = {
            'headers': {
                'Cache-Control': 'no-cache'
            },
            'timeout': 5
        }
        # yapf: enable
        self.assertEqual(call_kwargs, expected_call_kwargs)

        # Ensure system allocation email notification is correct
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.tech_lead.email])
        self.assertNotEqual(
            email.subject.find('Project scw0000 Deactivated'), -1
        )
        self.assertNotEqual(
            email.body.find(
                'Your Supercomputing Wales project scw0000 has been suspended.'
            ), -1
        )
        self.assertNotEqual(email.body.find(self.tech_lead.first_name), -1)

    # yapf: disable
    @mock.patch(
        'requests.put',
        side_effect=[OpenLDAPProjectAPITests.mock_reactivate_project_response()]
    )
    # yapf: enable
    def test_system_allocation_request_ldap_reactivation(self, post_mock):
        """
        Ensure the correct LDAP API url is called and email notification is 
        issued when re-activating a system allocation request.
        """
        # Approved projects must have a gid_number
        self.project.gid_number = 111111
        self.project.save()

        system_allocation_request = SystemAllocationRequest(
            project=self.project,
            start_date='2019-07-30',
            end_date='2019-09-30',
            status=SystemAllocationRequest.SUSPENDED
        )
        system_allocation_request.save()

        form = SystemAllocationRequestAdminForm(
            data={
                'project': self.project.id,
                'start_date': '2019-07-30',
                'end_date': '2019-09-30',
                'status': SystemAllocationRequest.APPROVED
            },
            instance=system_allocation_request
        )
        self.assertTrue(form.is_valid())

        # Approve system allocation request and trigger LDAP API calls
        form.save()

        # Ensure args passed to LDAP to re-activate a project are correct
        call_args, call_kwargs = post_mock.call_args_list[0]
        call_url = call_args[0]
        expected_call_url = f'{settings.OPENLDAP_HOST}project/enable/scw0000/'
        self.assertEqual(call_url, expected_call_url)
        # yapf: disable
        expected_call_kwargs = {
            'headers': {
                'Cache-Control': 'no-cache'
            },
            'timeout': 5
        }
        # yapf: enable
        self.assertEqual(call_kwargs, expected_call_kwargs)

        # Ensure system allocation email notification is correct
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.tech_lead.email])
        self.assertNotEqual(email.subject.find('Project scw0000 Activated'), -1)
        self.assertNotEqual(
            email.body.find(
                'Your Supercomputing Wales project scw0000 has been approved.'
            ), -1
        )
        self.assertNotEqual(email.body.find(self.tech_lead.first_name), -1)


class ProjectFormTestCase(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def setUp(self):
        self.title = "Example project title"
        self.institution = Institution.objects.get(name='Example University')
        self.project_code = 'scw0000'
        self.project = Project.objects.get(code=self.project_code)
        self.project_owner = self.project.tech_lead
        self.project_applicant = CustomUser.objects.get(
            email='admin.user@example.ac.uk'
        )

        # Create users for each institution
        self.institution_names, self.institution_users = CustomUserTests.create_institutional_users(
        )


class ProjectFormTests(ProjectFormTestCase):

    def setUp(self):
        super().setUp()
        institution = self.institution_names[0]
        self.user = self.institution_users[institution]
        self.data = {
            'title': 'Test Project',
            'description': 'A test project',
            'institution_reference': 'X',
            'department': 'Testing Department',
            'supervisor_name': 'supervisor',
            'supervisor_position': 'Researcher',
            'supervisor_email': 'supervisor@example.ac.uk',
        }
        self.form = ProjectCreationForm(self.user, self.data)

    def test_project_form_arcca_field(self):
        for i in self.institution_names:
            user = self.institution_users[i]
            form = ProjectCreationForm(user)
            if user.profile.institution.base_domain == 'cardiff.ac.uk':
                self.assertTrue('legacy_arcca_id' in form.fields)
            else:
                self.assertFalse('legacy_arcca_id' in form.fields)

    def test_project_form_valid(self):
        self.assertTrue(self.form.is_valid())

    def test_project_form_bad_supervisor_email(self):
        self.form.data['supervisor_email'] = 'supervisor at gmail.com'
        self.assertFalse(self.form.is_valid())

    def test_project_form_bad_supervisor_domain(self):
        self.form.data['supervisor_email'] = 'supervisor@gmail.com'
        self.assertFalse(self.form.is_valid())

    def test_project_form_external_user(self):
        self.user.profile.institution = None
        self.user = CustomUser.objects.get(email='guest.user@external.ac.uk')
        self.form = ProjectCreationForm(self.user, self.data)
        self.assertFalse(self.form.is_valid())


class AllocationRequestFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def setUp(self):
        self.title = "Example project title"
        # Create users for each institution
        self.institution_names, self.institution_users = CustomUserTests.create_institutional_users(
        )

        self.project_code = 'scw0000'
        self.project = Project.objects.get(code=self.project_code)
        self.user = self.project.tech_lead
        self.data = {
            'information': 'A test allocation',
            'start_date': '01/09/1985',
            'end_date': '01/09/1985',
            'allocation_cputime': '5',
            'allocation_memory': '1',
            'allocation_storage_home': '23',
            'allocation_storage_scratch': '65',
            'requirements_software': '',
            'requirements_training': '',
            'requirements_onboarding': '',
            'document': None,
            'attributions': [],
            'project': self.project.id,
        }

    def test_project_allocation_form_arcca_field(self):
        for i in self.institution_names:
            user = self.institution_users[i]
            form = SystemAllocationRequestCreationForm(user)
            if user.profile.institution.base_domain == 'cardiff.ac.uk':
                self.assertTrue('legacy_arcca_id' in form.fields)
            else:
                self.assertFalse('legacy_arcca_id' in form.fields)

    def test_project_allocation_form_validation(self):
        self.form = SystemAllocationRequestCreationForm(
            self.user, data=self.data
        )
        self.assertTrue(self.form.is_valid())

    def test_project_allocation_form_without_project(self):
        self.form = SystemAllocationRequestCreationForm(
            self.user, include_project=False, data=self.data
        )
        self.assertFalse('project' in self.form.fields)

    def test_project_allocation_form_other_project(self):
        self.project = Project.objects.get(code='scw0001')
        self.data['project'] = self.project.id
        self.form = SystemAllocationRequestCreationForm(
            self.user, project=self.project, data=self.data
        )
        self.assertFalse(self.form.is_valid())


class ProjectManageAttributionFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def setUp(self):
        self.title = "Example project title"
        # Create users for each institution
        self.institution_names, self.institution_users = CustomUserTests.create_institutional_users(
        )

        self.project_code = 'scw0000'
        self.project = Project.objects.get(code=self.project_code)
        self.user = self.project.tech_lead
        self.data = {
            'attributions': [],
        }

    def test_project_allocation_form_validation(self):
        self.form = ProjectManageAttributionForm(
            self.user, data=self.data, instance=self.project
        )
        self.assertTrue(self.form.is_valid())


class ProjectSupervisorApproveFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'funding/fixtures/tests/funding_bodies.json',
        'funding/fixtures/tests/attributions.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
    ]

    def setUp(self):
        self.project = Project.objects.get(code='scw0000')
        self.user = CustomUser.objects.get(email=self.project.supervisor_email)
        self.data = {
            'approved_by_supervisor': True,
        }

    def test_project_supervisor_form_validation(self):
        self.form = ProjectSupervisorApproveForm(
            self.user, instance=self.project, data=self.data
        )
        self.assertTrue(self.form.is_valid())

    def test_project_supervisor_form_incorrect_email(self):
        user = CustomUser.objects.get(email='guest.user@external.ac.uk')
        self.form = ProjectSupervisorApproveForm(
            user, instance=self.project, data=self.data
        )
        self.assertFalse(self.form.is_valid())


class ProjectUserRequestMembershipFormTests(ProjectFormTestCase):

    def test_request_membership_form_with_valid_data(self):
        pass

    def test_request_membership_form_with_an_invalid_user_id(self):
        """
        Ensure it is not possible to create a project user request membership with an invalid user id.
        """
        pass

    def test_request_membership_form_with_an_invalid_project_id(self):
        """
        Ensure it is not possible to create a project user request membership with an invalid project id.
        """
        pass


class ProjectUserMembershipCreationFormTests(ProjectFormTestCase):

    # Project are no longer approved, allocations are. Members can be added immediately
    # when a project is created.
    # @classmethod
    # def approve_project(cls, project):
    #     """
    #     The approval process will trigger the creation of a project user membership for the
    #     technical lead user see project/signals.py.
    #     Args:
    #         project (Project): Project to approve.
    #     """
    #     project.status = Project.APPROVED
    #     project.save()

    def test_form_when_project_is_awaiting_approval(self):
        """
        Project are no longer approved, allocations are. Members can be added immediately
        when a project is created.

        Ensure it is not possible to create a project user membership whilst the project is
        currently awaiting approval.
        """
        pass
        # form = ProjectUserMembershipCreationForm(
        #     initial={
        #         'user': self.project_applicant,
        #     },
        #     data={
        #         'project_code': self.project_code,
        #     },
        # )
        # self.assertFalse(form.is_valid())
        # self.assertEqual(
        #     form.errors['project_code'],
        #     ['The project is currently awaiting approval.'],
        # )

    def test_form(self):
        """
        Ensure it is possible to create a project user membership.
        """
        # self.approve_project(self.project)

        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': self.project_code,
            },
        )
        self.assertTrue(form.is_valid())

    def test_form_with_an_invalid_project_code(self):
        """
        Ensure it is not possible to create a project user membership using an invalid project code.
        """
        # self.approve_project(self.project)

        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': 'invalid-project-code',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['Invalid Project Code.'],
        )

    def test_form_with_an_authorised_project_member(self):
        """
        Ensure it is not possible to create a project user membership when a user is an
        authorised member of the project. By default, when the project is approved, a project user
        membership will be created for the technical lead.
        """
        accounts = [
            self.project_owner,
            # self.project_applicant,
        ]

        # Authorise a project user membership for the project applicant.
        ProjectUserMembership.objects.create(
            project=self.project,
            user=self.project_applicant,
            status=ProjectUserMembership.AUTHORISED,
            date_joined=datetime.datetime.now(),
            date_left=datetime.datetime.now() + datetime.timedelta(days=10),
        )

        for account in accounts:
            # self.approve_project(self.project)
            # A request to create a project user membership should be rejected.
            form = ProjectUserMembershipCreationForm(
                initial={
                    'user': account,
                },
                data={
                    'project_code': self.project_code,
                },
            )
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors['project_code'],
                ['You are currently a member of the project.'],
            )

            # Ensure the project user membership status is currently set authorised.
            membership = ProjectUserMembership.objects.get(user=account)
            self.assertTrue(membership.is_authorised())

    def test_form_when_a_user_has_a_request_awaiting_authorisation(self):
        """
        Ensure it is not possible to create a project user membership when a user has a
        membership request awaiting authorisation.
        """
        # self.approve_project(self.project)

        # Create a project user membership.
        ProjectUserMembership.objects.create(
            project=self.project,
            user=self.project_applicant,
            status=ProjectUserMembership.AWAITING_AUTHORISATION,
            date_joined=datetime.datetime.now(),
            date_left=datetime.datetime.now() + datetime.timedelta(days=10),
        )

        # Ensure the project user membership status is currently set to awaiting authorisation.
        membership = ProjectUserMembership.objects.get(
            user=self.project_applicant,
            project=self.project,
        )
        self.assertTrue(membership.is_awaiting_authorisation())

        # A request to create a project user membership should be rejected.
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': self.project_code,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['A membership request for this project already exists.'],
        )

    def test_form_when_project_code_is_greater_than_maximum_length(self):
        """
        Ensure the user is returned the correct error message when the project code is greater
        than the fields maximum length (20 chars).
        """
        # self.approve_project(self.project)

        invalid_project_code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=21)
        )
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': invalid_project_code,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['Ensure this value has at most 20 characters (it has 21).'],
        )


class ProjectUserInviteFormTests(ProjectFormTestCase):

    # Project are no longer approved, allocations are. Members can be added immediately
    # when a project is created.
    # @classmethod
    # def approve_project(cls, project):
    #     """
    #     The approval process will trigger the creation of a project user membership for the
    #     technical lead user see project/signals.py.
    #     Args:
    #         project (Project): Project to approve.
    #     """
    #     project.status = Project.APPROVED
    #     project.save()

    def test_form_when_project_is_awaiting_approval(self):
        """
        Project are no longer approved, allocations are. Members can be added immediately
        when a project is created.

        Ensure it is not possible to create a project user membership whilst the project is
        currently awaiting approval.
        """
        pass
        # form = ProjectUserInviteForm(
        #     initial={
        #         'project_id': 1,
        #     },
        #     data={
        #         'email': self.project_applicant.email,
        #     },
        # )
        # self.assertFalse(form.is_valid())

    def test_form(self):
        """
        Ensure it is possible to create a project user membership.
        """
        # self.approve_project(self.project)

        form = ProjectUserInviteForm(
            initial={
                'project_id': 1,
            },
            data={
                'email': self.project_applicant.email,
            },
        )
        self.assertTrue(form.is_valid())

    def test_form_with_an_authorised_project_member(self):
        """
        Ensure it is not possible to create a project user membership when a user is an
        authorised member of the project. By default, when the project is approved, a project user
        membership will be created for the technical lead.
        """
        accounts = [
            self.project_owner,
        ]

        for account in accounts:
            # Create a project.
            code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
            project = Project.objects.get(code="scw0000")
            # self.approve_project(project)

            # A request to create a project user membership should be rejected.
            form = ProjectUserInviteForm(
                initial={
                    'project_id': project.id,
                },
                data={
                    'email': account.email,
                },
            )
            self.assertFalse(form.is_valid())

            # Ensure the project user membership status is currently set authorised.
            membership = ProjectUserMembership.objects.get(
                user=account, project=project
            )
            self.assertTrue(membership.is_authorised())

    def test_form_when_a_user_has_a_request_awaiting_authorisation(self):
        """
        Ensure it is not possible to create a project user membership when a user has a
        membership request awaiting authorisation.
        """
        # Create a project.
        code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )
        project = Project.objects.get(code="scw0000")
        # self.approve_project(project)

        # Create a project user membership.
        ProjectUserMembership.objects.create(
            project=project,
            user=self.project_applicant,
            status=ProjectUserMembership.AWAITING_AUTHORISATION,
            date_joined=datetime.datetime.now(),
            date_left=datetime.datetime.now() + datetime.timedelta(days=10),
        )

        # Ensure the project user membership status is currently set to awaiting authorisation.
        membership = ProjectUserMembership.objects.get(
            user=self.project_applicant,
            project=project,
        )
        self.assertTrue(membership.is_awaiting_authorisation())

        # A request to create a project user membership should be rejected.
        form = ProjectUserInviteForm(
            initial={
                'project_id': 1,
            },
            data={
                'email': self.project_applicant.email,
            },
        )
        self.assertFalse(form.is_valid())

    def test_form_when_user_is_not_found(self):
        """
        Ensure it is not possible to create a project user membership when the use does
        not exist.
        """
        # Create a project.
        project = Project.objects.get(code="scw0000")

        # A request to create a project user membership should be rejected.
        form = ProjectUserInviteForm(
            initial={
                'project_id': project.id,
            },
            data={
                'email': 'user_does_not_exist@example.ac.uk',
            },
        )
        self.assertFalse(form.is_valid())


class SystemAllocationRequestCreationFormTests(ProjectFormTestCase):

    def test_form_with_unauthorized_project(self):
        """
        Ensure it is not possible to create a project user membership whilst the project is
        currently awaiting approval.
        """
        form = SystemAllocationRequestCreationForm(
            self.project_applicant,
            data={
                'project': 1,
                'information': '',
                'start_date': datetime.datetime.now(),
                'end_date': datetime.datetime.now(),
                'allocation_cputime': 1,
                'allocation_memory': 1,
                'allocation_storage_home': 1,
                'allocation_storage_scratch': 1,
                'requirements_software': '',
                'requirements_training': '',
                'requirements_onboarding': '',
                'document': '',
            },
        )
        self.assertFalse(form.is_valid())


class RSEAllocationRequestCreationFormTests(ProjectFormTestCase):
    default_data = {
        'title': 'Project to implement a management system',
        'duration': 1,
        'information': 'Supercomputing Wales is a programme',
        'goals': 'Allow users to sign up for the service.',
        'software': 'A Django-based website.',
        'outcomes': 'We get more users.',
        'confidentiality': 'Secret keys must be kept private.',
        'project': 1
    }

    def test_valid_form(self):
        user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        form = RSEAllocationRequestCreationForm(user, data=self.default_data)
        form.is_valid()
        self.assertTrue(form.is_valid())

    def test_invalid_durations(self):
        for duration in (0, -0.5, 0.00001, float('NaN')):
            form = RSEAllocationRequestCreationForm(
                CustomUser.objects.get(email='shibboleth.user@example.ac.uk'),
                data={
                    **self.default_data, 'duration': duration
                }
            )
            self.assertFalse(form.is_valid())

    def test_unauthorised(self):
        form = RSEAllocationRequestCreationForm(
            self.project_applicant, data=self.default_data
        )
        self.assertFalse(form.is_valid())

    def test_save_no_email(self):
        user = CustomUser.objects.get(email='test.user@example3.ac.uk')
        data = dict(self.default_data)
        data['project'] = 3
        form = RSEAllocationRequestCreationForm(user, data=data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertTrue(instance.project.id == 3)
        instance.delete()

    def test_save_with_email(self):
        form = RSEAllocationRequestCreationForm(
            CustomUser.objects.get(email='shibboleth.user@example.ac.uk'),
            data=self.default_data
        )
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertTrue(instance.project.id == 1)
        instance.delete()
