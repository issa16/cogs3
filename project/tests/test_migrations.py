from django.test import TestCase

from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.core import serializers

from funding.tests.test_migrations import TestMigration


class TestMigrationToFunding(TestMigration):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'project/fixtures/tests/categories.json',
    ]

    fixtures_before = [
        'project/fixtures/tests/phase1/projects_0041.json',
    ]

    migrate_from = [('project','0041_auto_20180731_1239')]
    migrate_to = [('project','0043_historicalsystemallocationrequest')]

    def test_migrated(self):
        Project = self.apps.get_model('project', 'Project')
        SystemAllocationRequest = self.apps.get_model('project', 'SystemAllocationRequest')

        # Get the project descriped in the 0041 fixture and the corresponding allocation
        project = Project.objects.get(id=1)
        allocation = SystemAllocationRequest.objects.get(project=project)

        # Check that necessary data got copied correctly
        self.assertEqual(allocation.start_date, project.start_date)
        self.assertEqual(allocation.end_date, project.end_date)
        self.assertEqual(allocation.allocation_rse, project.allocation_rse)
        self.assertEqual(allocation.allocation_cputime, project.allocation_cputime)
        self.assertEqual(allocation.allocation_memory, project.allocation_memory)
        self.assertEqual(allocation.allocation_storage_home, project.allocation_storage_home)
        self.assertEqual(allocation.allocation_storage_scratch, project.allocation_storage_scratch)
        self.assertEqual(allocation.status, project.status)
        self.assertEqual(allocation.previous_status, project.previous_status)
        self.assertEqual(allocation.reason_decision, project.reason_decision)
        self.assertEqual(allocation.requirements_software, project.requirements_software)
        self.assertEqual(allocation.requirements_training, project.requirements_training)
        self.assertEqual(allocation.requirements_onboarding, project.requirements_onboarding)
        self.assertEqual(allocation.document, project.document)
        self.assertEqual(allocation.notes, project.notes)

        
