from django.test import TestCase

from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.core import serializers

from project.models import Project


class TestMigrations(TestCase):

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = self.migrate_from
        self.migrate_to = self.migrate_to
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass


class TestMigrationToFunding(TestMigrations):

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

    def load_fixture(self, apps, fixture_file):
        original_apps = serializers.python.apps
        serializers.python.apps = apps
        fixture = open(fixture_file)
        objects = serializers.deserialize('json', fixture, ignorenonexistent=True)
        for obj in objects:
            obj.save()
        fixture.close()
        serializers.python.apps = original_apps

    def setUpBeforeMigration(self, apps):
        for fixture in self.fixtures_before:
            self.load_fixture(apps, fixture)
        Project = apps.get_model('project', 'Project')
        project = Project.objects.first()
        print(project)
        print(project.funding_source)

    def test_migrated(self):
        # Get the project descriped in the phase 1 fixture
        project = Project.objects.get(id=1)

        # The project should have one funding source
        funding_source = project.funding_sources.all().get()

        # Any meaningful content should be copied over
        self.assertEqual(funding_source.title, '')
        self.assertEqual(funding_source.identifier, '')
        self.assertEqual(funding_source.created_by, project.tech_lead)
        # The pi is left empty, may not be project pi or tech lead
        # self.assertEqual(funding_source.pi, project.tech_lead)

        # The funding source should refer to a funding body
        funding_body = funding_source.funding_body

        # Essentially this is the original funding source"
        self.assertEqual(funding_body.name, 'Test')
        self.assertEqual(funding_body.description, 'Test funding source')
