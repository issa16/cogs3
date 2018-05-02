import datetime
import random
import string

from django.contrib.auth.models import Group
from django.test import TestCase

from institution.tests.test_models import InstitutionTests
from project.forms import ProjectUserMembershipCreationForm
from project.models import Project
from project.models import ProjectUserMembership
from project.tests.test_models import ProjectCategoryTests
from project.tests.test_models import ProjectFundingSourceTests
from project.tests.test_models import ProjectTests
from users.tests.test_models import CustomUserTests


class ProjectFormTests(TestCase):

    def setUp(self):
        # Create an institution.
        base_domain = 'bangor.ac.uk'
        self.institution = InstitutionTests.create_institution(
            name='Bangor University',
            base_domain=base_domain,
        )

        # Create a project owner.
        group = Group.objects.get(name='project_owner')
        project_owner_email = '@'.join(['project_owner', base_domain])
        self.project_owner = CustomUserTests.create_custom_user(
            email=project_owner_email,
            group=group,
        )

        # Create a project applicant.
        project_applicant_email = '@'.join(['project_applicant', base_domain])
        self.project_applicant = CustomUserTests.create_custom_user(email=project_applicant_email)

        self.category = ProjectCategoryTests.create_project_category()
        self.funding_source = ProjectFundingSourceTests.create_project_funding_source()

        # Create a project.
        self.title = 'Project title'
        self.code = 'scw-00001',
        self.project = ProjectTests.create_project(
            title=self.title,
            code=self.code,
            institution=self.institution,
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )

        # Ensure no project user membership requests have been created.
        self.assertEqual(ProjectUserMembership.objects.count(), 0)


class ProjectUserRequestMembershipFormTests(ProjectFormTests, TestCase):

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


class ProjectUserMembershipCreationFormTests(ProjectFormTests, TestCase):

    def approve_project(self, project):
        """
        The approval process will trigger the creation of a project user membership for the
        technical lead user see project/signals.py.

        Args:
            project (Project): Project to approve.
        """
        project.status = Project.APPROVED
        project.save()

    def test_form_when_project_is_awaiting_approval(self):
        """
        Ensure it is not possible to create a project user membership whilst the project is
        currently awaiting approval.
        """
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': self.code,
            },
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['The project is currently awaiting approval.'],
        )

    def test_form_after_the_project_has_been_approved(self):
        """
        Ensure it is possible to create a project user membership after the project has been approved.
        """
        self.approve_project(self.project)

        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': self.code,
            },
        )
        self.assertTrue(form.is_valid())

    def test_form_with_an_invalid_project_code(self):
        """
        Ensure it is not possible to create a project user membership using an invalid project code.
        """
        self.approve_project(self.project)

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
            ['Invalid SCW project code.'],
        )

    def test_form_with_an_authorised_project_member(self):
        """
        Ensure it is not possible to create a project user membership when a user is an 
        authorised member of the project. By default, when the project is approved, a project user
        membership will be created for the technical lead.
        """
        accounts = [
            self.project_owner,
            self.project_applicant,
        ]

        for account in accounts:
            # Create a project.
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            project = ProjectTests.create_project(
                title=self.title,
                code='scw-' + code,
                institution=self.institution,
                tech_lead=account,
                category=self.category,
                funding_source=self.funding_source,
            )
            self.approve_project(project)

            # A request to create a project user membership should be rejected.
            form = ProjectUserMembershipCreationForm(
                initial={
                    'user': account,
                },
                data={
                    'project_code': project.code,
                },
            )
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors['project_code'],
                ['You are currently a member of the project.'],
            )

            # Ensure the project user membership status is currently set authorised.
            membership = ProjectUserMembership.objects.get(user=account)
            self.assertTrue(membership.authorised())

    def test_form_when_a_user_has_a_request_awaiting_authorisation(self):
        """
        Ensure it is not possible to create a project user membership when a user has a
        membership request awaiting authorisation.
        """
        # Create a project.
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        project = ProjectTests.create_project(
            title=self.title,
            code='scw-' + code,
            institution=self.institution,
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )
        self.approve_project(project)

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
        self.assertTrue(membership.awaiting_authorisation())

        # A request to create a project user membership should be rejected.
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.project_applicant,
            },
            data={
                'project_code': project.code,
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
        self.approve_project(self.project)

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
