import datetime

from django.test import TestCase

from institution.tests.test_models import InstitutionTests
from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectFundingSource
from project.models import ProjectSystemAllocation
from project.models import ProjectUserMembership
from system.tests.test_models import SystemTests
from users.tests.test_models import CustomUserTests


class ProjectFundingSourceTests(TestCase):

    def create_project_funding_source(self):
        project_funding_source = ProjectFundingSource.objects.create(
            name='A project function source name',
            description='A project funding source description',
        )
        return project_funding_source

    def test_project_funding_source_creation(self):
        project_funding_source = self.create_project_funding_source()
        self.assertTrue(isinstance(project_funding_source, ProjectFundingSource))
        self.assertEqual(project_funding_source.__str__(), project_funding_source.name)


class ProjectCategoryTests(TestCase):

    def create_project_category(self):
        project_category = ProjectCategory.objects.create(
            name='A project category name',
            description='A project category description',
        )
        return project_category

    def test_project_category_creation(self):
        project_category = self.create_project_category()
        self.assertTrue(isinstance(project_category, ProjectCategory))
        self.assertEqual(project_category.__str__(), project_category.name)


class ProjectModelTests(TestCase):

    def setUp(self):
        # Create an institution
        self.institution = InstitutionTests().create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
        )

        # Create a technical lead user account
        self.tech_lead = CustomUserTests().create_techlead_user(
            username='scw_techlead@bangor.ac.uk',
            password='123456',
        )

        # Create a student user account
        self.student = CustomUserTests().create_student_user(
            username='scw_student@bangor.ac.uk',
            password='123456',
        )

        self.category = ProjectCategoryTests().create_project_category()
        self.funding_source = ProjectFundingSourceTests().create_project_funding_source()


class ProjectTests(ProjectModelTests, TestCase):

    def create_project(self, title, code, institution, tech_lead, category, funding_source):
        project = Project.objects.create(
            title=title,
            description='Project description',
            legacy_hpcw_id='HPCW-12345',
            legacy_arcca_id='ARCCA-12345',
            code=code,
            institution=institution,
            institution_reference='BW-12345',
            pi='Project Principal Investigator',
            tech_lead=tech_lead,
            category=category,
            funding_source=funding_source,
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() + datetime.timedelta(days=10),
            economic_user=True,
            requirements_software='None',
            requirements_gateways='None',
            requirements_training='None',
            requirements_onboarding='None',
            allocation_rse=True,
            allocation_cputime='1000000',
            allocation_storage='1000',
            notes='Project notes',
        )
        return project

    def test_project_creation(self):
        title = 'Project title'
        code = 'SCW-12345'
        project = self.create_project(
            title=title,
            code=code,
            institution=self.institution,
            tech_lead=self.tech_lead,
            category=self.category,
            funding_source=self.funding_source,
        )
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(project.__str__(), code + ' - ' + title)
        self.assertEqual(project.status, Project.AWAITING_APPROVAL)
        self.assertTrue(project.awaiting_approval())


class ProjectSystemAllocationTests(ProjectModelTests, TestCase):

    def setUp(self):
        super(ProjectSystemAllocationTests, self).setUp()
        self.project = ProjectTests().create_project(
            title='Project title',
            code='SCW-12345',
            institution=self.institution,
            tech_lead=self.tech_lead,
            category=self.category,
            funding_source=self.funding_source,
        )

        self.system = SystemTests().create_system(
            name='Nemesis',
            description='Bangor University Cluster',
            number_of_cores=10000,
        )

    def create_project_system_allocation(self):
        project_system_allocation = ProjectSystemAllocation.objects.create(
            project=self.project,
            system=self.system,
            date_allocated=datetime.datetime.now(),
            date_unallocated=datetime.datetime.now() + datetime.timedelta(days=10),
        )
        return project_system_allocation

    def test_project_system_allocation_creation(self):
        project_system_allocation = self.create_project_system_allocation()
        self.assertTrue(isinstance(project_system_allocation, ProjectSystemAllocation))
        data = {
            'project': self.project,
            'system': self.system,
            'date_allocated': project_system_allocation.date_allocated,
            'date_unallocated': project_system_allocation.date_unallocated
        }
        expected = '{project} on {system} from {date_allocated} to {date_unallocated}'.format(**data)
        self.assertEqual(project_system_allocation.__str__(), expected)


class ProjectUserMembershipTests(ProjectModelTests, TestCase):

    def setUp(self):
        super(ProjectUserMembershipTests, self).setUp()
        self.project = ProjectTests().create_project(
            title='Project title',
            code='SCW-12345',
            institution=self.institution,
            tech_lead=self.tech_lead,
            category=self.category,
            funding_source=self.funding_source,
        )
        self.membership = self.create_project_user_membership(
            user=self.student,
            project=self.project,
        )
        self.assertEqual(ProjectUserMembership.objects.filter(user=self.student).count(), 1)

    def create_project_user_membership(self, user, project):
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
        Ensure the awaiting_authorisation() method returns the correct response.
        """
        self.membership.status = ProjectUserMembership.AWAITING_AUTHORISATION
        self.assertTrue(self.membership.awaiting_authorisation())

        self.membership.status = ProjectUserMembership.AUTHORISED
        self.assertFalse(self.membership.awaiting_authorisation())

    def test_project_user_membership_authorised_status(self):
        """
        Ensure the authorised() method returns the correct response.
        """
        self.membership.status = ProjectUserMembership.AUTHORISED
        self.assertTrue(self.membership.authorised())

        self.membership.status = ProjectUserMembership.AWAITING_AUTHORISATION
        self.assertFalse(self.membership.authorised())

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
            self.assertTrue(self.membership.unauthorised())

    def test_project_user_membership_str_representation(self):
        data = {
            'user': self.student,
            'project': self.project,
            'date_joined': self.membership.date_joined,
            'date_left': self.membership.date_left
        }
        expected = '{user} on {project} from {date_joined} to {date_left}'.format(**data)
        self.assertEqual(self.membership.__str__(), expected)
