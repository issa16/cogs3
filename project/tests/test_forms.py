import datetime

from django import forms
from django.test import TestCase

from institution.tests import InstitutionTests
from project.forms import ProjectUserMembershipCreationForm
from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectFundingSource
from project.models import ProjectUserMembership
from project.tests.test_models import ProjectCategoryTests
from project.tests.test_models import ProjectFundingSourceTests
from project.tests.test_models import ProjectTests
from users.tests import CustomUserTests


class ProjectUserMembershipCreationFormTests(TestCase):

    def setUp(self):
        self.institution = InstitutionTests().create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
        )

        self.student = CustomUserTests().create_student_user(
            username='scw_student@bangor.ac.uk',
            password='123456',
        )
        self.tech_lead = CustomUserTests().create_techlead_user(
            username='scw_techlead@bangor.ac.uk',
            password='123456',
        )

        self.category = ProjectCategoryTests().create_project_category()
        self.funding_source = ProjectFundingSourceTests().create_project_funding_source()

        self.title = 'Project title'
        self.code = 'SCW-12345'
        self.project = ProjectTests().create_project(
            title=self.title,
            code=self.code,
            institution=self.institution,
            tech_lead=self.tech_lead,
            category=self.category,
            funding_source=self.funding_source,
        )
        self.assertEqual(ProjectUserMembership.objects.count(), 0)

    def approve_project(self, project):
        """
        The approval process will trigger the creation of a project user membership for the tech lead.
        """
        project.status = Project.APPROVED
        project.save()
        self.assertEqual(ProjectUserMembership.objects.count(), 1)

    def test_membership_creation_form_whilst_project_is_awaiting_approval(self):
        """
        It should not be possible to create a project user membership whilst the project is 
        currently awaiting approval.
        """
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.student,
            }, data={
                'project_code': self.code,
            })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['The project is currently awaiting approval.'],
        )

    def test_membership_creation_form_after_the_project_has_been_approved(self):
        """
        It should be possible to create a project user membership after the project has 
        been approved.
        """
        self.approve_project(self.project)
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.student,
            }, data={
                'project_code': self.code,
            })
        self.assertTrue(form.is_valid())

    def test_membership_creation_form_with_invalid_project_code(self):
        """
        It should not be possible to create a project user membership using an invalid 
        project code.
        """
        self.approve_project(self.project)
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.student,
            }, data={
                'project_code': 'invalid-project-code',
            })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['Invalid SCW project code.'],
        )

    def test_membership_creation_form_when_a_techlead_is_already_a_member(self):
        """
        It should not be possible to create a project user membership when a techlead is 
        already a member of the project.
        """
        self.approve_project(self.project)

        # The second request to create a project user membership should be rejected
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.tech_lead,
            }, data={
                'project_code': self.code
            })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['You are currently a member of the project.'],
        )

    def test_membership_creation_form_when_a_student_already_has_a_pending_membership_request(self):
        """
        It should not be possible to create a project user membership when a student already has 
        a pending project user membership request.
        """
        self.approve_project(self.project)

        # Create a project user membership
        ProjectUserMembership.objects.create(
            project=self.project,
            user=self.student,
            status=ProjectUserMembership.AWAITING_AUTHORISATION,
            date_joined=datetime.datetime.now(),
            date_left=datetime.datetime.now() + datetime.timedelta(days=10),
        )
        self.assertEqual(ProjectUserMembership.objects.filter(user=self.student).count(), 1)

        # The second request to create a project user membership should be rejected
        form = ProjectUserMembershipCreationForm(
            initial={
                'user': self.student,
            }, data={
                'project_code': self.code
            })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['project_code'],
            ['A membership request for this project already exists.'],
        )
        self.assertEqual(ProjectUserMembership.objects.filter(user=self.student).count(), 1)
