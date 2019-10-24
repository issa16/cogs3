import datetime

from django.contrib.auth.models import Group
from django.test import TestCase

from institution.models import Institution
from funding.tests.test_models import FundingBodyTests
from funding.tests.test_models import FundingSourceTests
from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectSystemAllocation
from project.models import ProjectUserMembership
from system.models import System
from users.tests.test_models import CustomUserTests


class ProjectCategoryTests(TestCase):

    @classmethod
    def create_project_category(cls, name, description):
        """
        Create a ProjectCategory instance.

        Args:
            name (str): Project category name.
            description (str): Project category description.
        """
        return ProjectCategory.objects.create(
            name=name,
            description=description,
        )

    def test_project_category_creation(self):
        """
        Ensure we can create a ProjectCategory instance.
        """
        name = 'A project category name'
        description = 'A project category description'
        project_category = self.create_project_category(
            name=name,
            description=description,
        )
        self.assertTrue(isinstance(project_category, ProjectCategory))
        self.assertEqual(project_category.__str__(), project_category.name)
        self.assertEqual(project_category.name, name)
        self.assertEqual(project_category.description, description)


class ProjectModelTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')

        # Create a project owner.
        group = Group.objects.get(name='project_owner')
        project_owner_email = '@'.join([
            'project_owner', self.institution.base_domain
        ])
        self.project_owner = CustomUserTests.create_custom_user(
            email=project_owner_email,
            group=group,
        )

        # Create a project applicant.
        project_applicant_email = '@'.join([
            'project_applicant', self.institution.base_domain
        ])
        self.project_applicant = CustomUserTests.create_custom_user(
            email=project_applicant_email
        )

        # Create a project category
        name = 'A project category name'
        description = 'A project category description'
        self.category = ProjectCategoryTests.create_project_category(
            name=name,
            description=description,
        )

        # Create a funding body
        name = 'A funding source name'
        description = 'A funding source description'
        self.funding_body = FundingBodyTests.create_funding_body(
            name=name,
            description=description,
        )

        # Create a funding source
        title = 'A funding source title'
        identifier = 'A funding source identifier'
        pi_email = '@'.join(['pi', self.institution.base_domain])
        self.funding_source = FundingSourceTests.create_funding_source(
            title=title,
            identifier=identifier,
            funding_body=self.funding_body,
            owner=self.project_owner,
            pi_email=pi_email,
            amount=1000,
        )


class ProjectTests(ProjectModelTests, TestCase):

    @classmethod
    def create_project(cls, title, code, tech_lead, category, funding_source):
        """
        Create a Project instance.

        Args:
            title (str): Project title.
            code (str): Project code.
            institution (Institution): Institution project is based.
            tech_lead (settings.AUTH_USER_MODEL): Project technical lead user.
            category (ProjectCategory): Project category.
            funding_source (FundingSource): Project funding source.
        """
        project = Project.objects.create(
            title=title,
            description='Project description',
            legacy_hpcw_id='HPCW-12345',
            legacy_arcca_id='ARCCA-12345',
            code=code,
            institution_reference='BW-12345',
            department='School of Chemistry',
            supervisor_name="Joe Bloggs",
            supervisor_position="RSE",
            supervisor_email="joe.bloggs@swansea.ac.uk",
            tech_lead=tech_lead,
            category=category,
            economic_user=True
        )
        project.attributions.set([funding_source.attribution_ptr])
        return project

    def _verify_project_details(self, project, title, code):
        """
        Ensure project details are correct.
        """
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(project.__str__(), code)
        self.assertEqual(project.title, title)
        self.assertEqual(project.code, code)
        #self.assertEqual(project.status, Project.AWAITING_APPROVAL)
        #self.assertTrue(project.is_awaiting_approval())

    def test_project_creation(self):
        """
        Ensure we can create a Project instance.
        """
        title = 'Project title'
        code = 'SCW-12345'
        project = self.create_project(
            title=title,
            code=code,
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )
        self._verify_project_details(project, title, code)

    def test_project_creation_with_duplicate_titles(self):
        """
        A test to ensure a project can be created when the title exists in the database.

        Issues:
            - https://github.com/tystakartografen/cogs3/issues/30
            - https://github.com/tystakartografen/cogs3/issues/31
        """
        title_1 = 'Project title'
        code_1 = 'SCW-0001'
        project_1 = self.create_project(
            title=title_1,
            code=code_1,
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )

        title_2 = 'Project title'
        code_2 = 'SCW-0002'
        project_2 = self.create_project(
            title=title_2,
            code=code_2,
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )
        self._verify_project_details(project_1, title_1, code_1)
        self._verify_project_details(project_2, title_2, code_2)
        self.assertEqual(Project.objects.count(), 2)

    def test_project_tech_lead_membership(self):
        """
        Check that the a membership is correctly created when a project is saved
        """
        title = 'Project title'
        code = 'SCW-12345'
        project = self.create_project(
            title=title,
            code=code,
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )
        project.save()

        # The tech lead should have been added to project_owner
        group = self.project_owner.groups.filter(name='project_owner')
        self.assertTrue(group.exists())

        # And a membership should have been created
        membership = ProjectUserMembership.objects.filter(
            user=self.project_owner, project=project
        )

        self.assertTrue(membership.exists())


class ProjectSystemAllocationTests(ProjectModelTests, TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'system/fixtures/tests/systems.json',
    ]

    def setUp(self):
        super(ProjectSystemAllocationTests, self).setUp()
        self.system = System.objects.get(name='Nemesis')

        # Create a project.
        self.project = ProjectTests.create_project(
            title='Project title',
            code='SCW-12345',
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )

    def test_project_system_allocation_creation(self):
        """
        Ensure we can create an ProjectSystemAllocation instance.
        """
        project_system_allocation = ProjectSystemAllocation.objects.create(
            project=self.project,
            system=self.system,
            date_allocated=datetime.datetime.now(),
            date_unallocated=datetime.datetime.now() +
            datetime.timedelta(days=10),
        )
        self.assertTrue(
            isinstance(project_system_allocation, ProjectSystemAllocation)
        )
        data = {
            'project': self.project,
            'system': self.system,
            'date_allocated': project_system_allocation.date_allocated,
            'date_unallocated': project_system_allocation.date_unallocated
        }
        expected = '{project} on {system} from {date_allocated} to {date_unallocated}'.format(
            **data
        )
        self.assertEqual(project_system_allocation.__str__(), expected)


class ProjectUserMembershipTests(ProjectModelTests, TestCase):

    def setUp(self):
        super(ProjectUserMembershipTests, self).setUp()

        # Create a project.
        self.project = ProjectTests.create_project(
            title='Project title',
            code='SCW-12345',
            tech_lead=self.project_owner,
            category=self.category,
            funding_source=self.funding_source,
        )

        # Create a project user membership.
        self.membership = self.create_project_user_membership(
            user=self.project_applicant,
            project=self.project,
        )

        self.assertEqual(
            ProjectUserMembership.objects.filter(user=self.project_applicant
                                                ).count(),
            1
        )

    @classmethod
    def create_project_user_membership(cls, user, project):
        """
        Create a ProjectUserMembership instance.

        Args:
            user (settings.AUTH_USER_MODEL): The user requesting to join the project.
            project (Project): The project the user is requesting to join.
        """
        project_user_membership = ProjectUserMembership.objects.create(
            project=project,
            user=user,
            status=ProjectUserMembership.AWAITING_AUTHORISATION,
            date_joined=datetime.datetime.now(),
            date_left=datetime.datetime.now() + datetime.timedelta(days=10),
        )
        return project_user_membership

    def test_project_user_membership_awaiting_authorisation_status(self):
        """
        Ensure the is_awaiting_authorisation() method returns the correct response.
        """
        self.membership.status = ProjectUserMembership.AWAITING_AUTHORISATION
        self.assertTrue(self.membership.is_awaiting_authorisation())

        self.membership.status = ProjectUserMembership.AUTHORISED
        self.assertFalse(self.membership.is_awaiting_authorisation())

    def test_project_user_membership_authorised_status(self):
        """
        Ensure the authorised() method returns the correct response.
        """
        self.membership.status = ProjectUserMembership.AUTHORISED
        self.assertTrue(self.membership.is_authorised())

        self.membership.status = ProjectUserMembership.AWAITING_AUTHORISATION
        self.assertFalse(self.membership.is_authorised())

    def test_project_user_membership_unauthorised_status(self):
        """
        Ensure the unauthorised() method returns the correct response.
        """
        unauthorised_states = [
            ProjectUserMembership.REVOKED,
            ProjectUserMembership.SUSPENDED,
            ProjectUserMembership.DECLINED,
        ]
        for status in unauthorised_states:
            self.membership.status = status
            self.assertTrue(self.membership.is_unauthorised())

    def test_project_user_membership_owner_editable(self):
        """
        Ensure the unauthorised() method returns the correct response.
        """
        disallowed_states = [
            ProjectUserMembership.AWAITING_AUTHORISATION,
            ProjectUserMembership.DECLINED,
        ]
        allowed_states = [
            ProjectUserMembership.AUTHORISED,
            ProjectUserMembership.REVOKED,
            ProjectUserMembership.SUSPENDED,
        ]
        self.membership.initiated_by_user = False
        for status in disallowed_states:
            self.membership.status = status
            self.assertFalse(self.membership.is_owner_editable())
        for status in allowed_states:
            self.membership.status = status
            self.assertTrue(self.membership.is_owner_editable())

        self.membership.initiated_by_user = True
        for status in disallowed_states + allowed_states:
            self.membership.status = status
            self.assertTrue(self.membership.is_owner_editable())

    def test_project_user_membership_user_editable(self):
        """
        Ensure the unauthorised() method returns the correct response.
        """
        disallowed_states = [
            ProjectUserMembership.REVOKED,
            ProjectUserMembership.SUSPENDED,
        ]
        allowed_states = [
            ProjectUserMembership.AWAITING_AUTHORISATION,
            ProjectUserMembership.AUTHORISED,
            ProjectUserMembership.DECLINED,
        ]
        self.membership.initiated_by_user = False
        for status in disallowed_states:
            self.membership.status = status
            self.assertFalse(self.membership.is_user_editable())
        for status in allowed_states:
            self.membership.status = status
            self.assertTrue(self.membership.is_user_editable())

        self.membership.initiated_by_user = True
        for status in disallowed_states + allowed_states:
            self.membership.status = status
            self.assertFalse(self.membership.is_user_editable())

    def test_project_user_membership_str_representation(self):
        data = {
            'user': self.project_applicant,
            'project': self.project,
            'date_joined': self.membership.date_joined,
            'date_left': self.membership.date_left
        }
        expected = '{user} on {project} from {date_joined} to {date_left}'.format(
            **data
        )
        self.assertEqual(self.membership.__str__(), expected)
