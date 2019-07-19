from django.test import TestCase

from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.core import serializers


class TestMigration(TestCase):

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "migrate_to and migrate_from must be defined"
        executor = MigrationExecutor(connection)
        apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        for fixture in self.fixtures_before:
            self.load_fixture(apps, fixture)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def load_fixture(self, apps, fixture_file):
        original_apps = serializers.python.apps
        serializers.python.apps = apps
        fixture = open(fixture_file)
        objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
        for obj in objects:
            obj.save()
        fixture.close()
        serializers.python.apps = original_apps


class TestMigrationToFunding(TestMigration):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
        'project/fixtures/tests/categories.json',
    ]

    fixtures_before = [
        'project/fixtures/tests/phase1/projectfundingsources.json',
        'project/fixtures/tests/phase1/projects.json',
    ]

    migrate_from = [('project','0035_auto_20180626_2111')]
    migrate_to = [('funding','0002_copy_fundingsource')]

    def test_migrated(self):
        Project = self.apps.get_model('project', 'Project')
        FundingSource = self.apps.get_model('funding', 'FundingSource')

        # Get the project descriped in the phase 1 fixture
        project = Project.objects.get(id=1)

        # The project should have one funding source
        attribution = project.attributions.all().get()

        # Any meaningful content should be copied over
        self.assertEqual(attribution.title, '')
        self.assertEqual(attribution.created_by, project.tech_lead)

        # The attribution should have a funding source
        fundingsource = FundingSource.objects.get(attribution_ptr=attribution)
        self.assertEqual(fundingsource.identifier, '')
        # The pi is left empty, may not be project pi or tech lead
        # self.assertEqual(fundingsource.pi, project.tech_lead)

        # The funding source should refer to a funding body
        funding_body = fundingsource.funding_body

        # Essentially this is the original funding source"
        self.assertEqual(funding_body.name, 'Test')
        self.assertEqual(funding_body.description, 'Test funding source')
