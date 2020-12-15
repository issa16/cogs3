from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from stats.models import StorageWeekly


class ImportWeeklyStorageTest(TestCase):

    fixtures = [
        'users/fixtures/tests/users.json',
        'project/fixtures/tests/funding_sources.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
        'system/fixtures/systems.json',
    ]

    def test_required_command_line_args(self):
        '''
        Ensure an error is displayed to the user if the required command line
        args are not supplied.
        '''
        with self.assertRaises(CommandError) as e:
            out = StringIO()
            call_command('import_weekly_storage', stdout=out)
        self.assertIn(
            'Error: the following arguments are required: --homefile, --scratchfile, -d, -m, -y, -s',
            str(e.exception),
        )

    def test_invalid_date(self):
        '''
        Ensure an error is displayed to the user if the date value is 
        not a Saturday.
        '''
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=valid.csv',
            '--scratchfile=valid.csv',
            '-d 20',
            '-m 11',
            '-y 2020',
            '-s CF',
            stdout=out
        )
        self.assertIn('is not a Saturday', out.getvalue())

    def test_invalid_system_code(self):
        '''
        Ensure an error is displayed to the user if the system code is invalid.
        '''
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=invalid.csv',
            '--scratchfile=valid.csv',
            '-d 21',
            '-m 11',
            '-y 2020',
            '-s INVALID',
            stdout=out
        )
        self.assertIn("System 'INVALID' not found", out.getvalue())

    def test_invalid_homefile_path(self):
        '''
        Ensure an error is displayed to the user if the path to the home
        file is invalid.
        '''
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=invalid_homefile.csv',
            '--scratchfile=/app/stats/tests/project_usage_scratch.csv',
            '-d 21',
            '-m 11',
            '-y 2020',
            '-s CF',
            stdout=out
        )
        self.assertIn('invalid_homefile.csv not found', out.getvalue())

    def test_invalid_scratchfile_path(self):
        '''
        Ensure an error is displayed to the user if the path to the scratch
        file is invalid.
        '''
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=/app/stats/tests/project_usage_home.csv',
            '--scratchfile=invalid_scratchfile.csv',
            '-d 21',
            '-m 11',
            '-y 2020',
            '-s CF',
            stdout=out
        )
        self.assertIn('invalid_scratchfile.csv not found', out.getvalue())

    def test_missing_project_codes(self):
        '''
        Ensure an error is displayed to the user if project codes
        are not found within the database.
        '''
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=/app/stats/tests/project_usage_home.csv',
            '--scratchfile=/app/stats/tests/project_usage_scratch.csv',
            '-d 21',
            '-m 11',
            '-y 2020',
            '-s CF',
            stdout=out
        )
        self.assertIn(
            'No matching database project scw0001...skipping',
            out.getvalue(),
        )
        self.assertIn(
            'No matching database project scw0002...skipping',
            out.getvalue(),
        )

    def test_missing_scratch_stat(self):
        '''
        Ensure an error is displayed to the user if scratch stats
        for a project are not found.
        '''
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=/app/stats/tests/project_usage_home.csv',
            '--scratchfile=/app/stats/tests/project_usage_scratch.csv',
            '-d 21',
            '-m 11',
            '-y 2020',
            '-s CF',
            stdout=out
        )
        self.assertIn(
            "Couldn't find scratch stats for scw0000...skipping",
            out.getvalue(),
        )

    def test_scw1000_storage_stats(self):
        '''
        Ensure storage stats for scw1000 are process correctly.
        '''
        self.assertEqual(StorageWeekly.objects.count(), 0)
        out = StringIO()
        call_command(
            'import_weekly_storage',
            '--homefile=/app/stats/tests/project_usage_home.csv',
            '--scratchfile=/app/stats/tests/project_usage_scratch.csv',
            '-d 21',
            '-m 11',
            '-y 2020',
            '-s CF',
            stdout=out
        )
        self.assertEqual(StorageWeekly.objects.count(), 1)
        scw1000_storage_stats = StorageWeekly.objects.get(project__code='scw1000')
        self.assertEqual(str(scw1000_storage_stats.system), 'Hawk')
        self.assertEqual(scw1000_storage_stats.home_space_used, 88)
        self.assertEqual(scw1000_storage_stats.home_files_used, 99)
        self.assertEqual(scw1000_storage_stats.scratch_space_used, 66)
        self.assertEqual(scw1000_storage_stats.scratch_files_used, 55)
