from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class ImportWeeklyStorageTest(TestCase):

    fixtures = ["system/fixtures/systems.json"]

    def test_required_command_line_args(self):
        with self.assertRaises(CommandError) as e:
            out = StringIO()
            call_command('import_weekly_storage', stdout=out)
        self.assertIn(
            'Error: the following arguments are required: --homefile, --scratchfile, -d, -m, -y, -s', str(e.exception)
        )

    def test_invalid_date(self):
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
