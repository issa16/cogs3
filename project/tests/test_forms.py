import datetime
import random
import string

from django.test import TestCase

from institution.models import Institution
from project.forms import ProjectCreationForm
from project.forms import ProjectUserMembershipCreationForm
from project.forms import ProjectUserInviteForm
from project.forms import RSEAllocationRequestCreationForm
from project.forms import SystemAllocationRequestCreationForm
from project.models import Project
from project.models import ProjectUserMembership
from users.models import CustomUser
from users.tests.test_models import CustomUserTests


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
        self.project_applicant = CustomUser.objects.get(email='admin.user@example.ac.uk')

        # Create users for each institution
        self.institution_names, self.institution_users = CustomUserTests.create_institutional_users()


class ProjectFormTests(ProjectFormTestCase):
    def setUp(self):
        super().setUp()
        institution = self.institution_names[0]
        user = self.institution_users[institution]
        self.data = {
            'title': 'Test Project',
            'description': 'A test project',
            'institution_reference': 'X',
            'department': 'Testing Department',
            'supervisor_name': 'supervisor',
            'supervisor_position': 'Researcher',
            'supervisor_email': 'supervisor@example.ac.uk',
        }
        self.form = ProjectCreationForm(user,self.data)


    def test_project_form_arcca_field(self):
        for i in self.institution_names:
            user = self.institution_users[i]
            form = ProjectCreationForm(user)
            if user.profile.institution.base_domain == 'cardiff.ac.uk':
                self.assertTrue('legacy_arcca_id' in form.fields)
            else:
                self.assertFalse('legacy_arcca_id' in form.fields)

    def test_project_form_valid(self):
        self.assertTrue( self.form.is_valid() )

    def test_project_form_supervisor_email(self):
        self.form.data['supervisor_email'] = 'supervisor@gmail.com'
        self.assertFalse( self.form.is_valid() )


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
        self.institution = Institution.objects.get(name='Example University')
        self.project_code = 'scw0000'
        self.project = Project.objects.get(code=self.project_code)
        self.project_owner = self.project.tech_lead
        self.project_applicant = CustomUser.objects.get(email='admin.user@example.ac.uk')

        # Create users for each institution
        self.institution_names, self.institution_users = CustomUserTests.create_institutional_users()

    def test_project_form_arcca_field(self):
        for i in self.institution_names:
            user = self.institution_users[i]
            form = SystemAllocationRequestCreationForm(user)


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

        invalid_project_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
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
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
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
            membership = ProjectUserMembership.objects.get(user=account, project=project)
            self.assertTrue(membership.is_authorised())

    def test_form_when_a_user_has_a_request_awaiting_authorisation(self):
        """
        Ensure it is not possible to create a project user membership when a user has a
        membership request awaiting authorisation.
        """
        # Create a project.
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
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
        form = RSEAllocationRequestCreationForm(
            CustomUser.objects.get(email='shibboleth.user@example.ac.uk'),
            data=self.default_data
        )
        self.assertTrue(form.is_valid())

    def test_invalid_durations(self):
        for duration in (0, -0.5, 0.00001, float('NaN')):
            form = RSEAllocationRequestCreationForm(
                CustomUser.objects.get(email='shibboleth.user@example.ac.uk'),
                data={**self.default_data, 'duration': duration}
            )
            self.assertFalse(form.is_valid())

    def test_unauthorised(self):
        form = RSEAllocationRequestCreationForm(
            self.project_applicant,
            data=self.default_data
        )
        self.assertFalse(form.is_valid())
        
