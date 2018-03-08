import datetime

from django.test import TestCase

from .models import Project
from .models import ProjectCategory
from .models import ProjectFundingSource
from institution.tests import InstitutionTests
from users.tests import CustomUserTests


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


class ProjectTests(TestCase):

    def setUp(self):
        self.institution = InstitutionTests().create_institution()
        self.tech_lead = CustomUserTests().create_techlead_user(username='scw_techlead')
        self.category = ProjectCategoryTests().create_project_category()
        self.funding_source = ProjectFundingSourceTests().create_project_funding_source()

    def test_project_creation(self):
        project = Project.objects.create(
            title='Project title',
            description='Project description',
            legacy_hpcw_id='HPCW-12345',
            legacy_arcca_id='ARCCA-12345',
            code='SCW-12345',
            institution=self.institution,
            institution_reference='BW-12345',
            pi='Project Principal Investigator',
            tech_lead=self.tech_lead,
            category=self.category,
            funding_source=self.funding_source,
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
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(project.__str__(), 'SCW-12345 - Project title')
        self.assertEqual(project.status, Project.AWAITING_APPROVAL)
