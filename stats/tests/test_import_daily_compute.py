from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from stats.models import ComputeDaily


class ImportDailyComputeTest(TestCase):

    fixtures = [
        'users/fixtures/tests/users.json',
        'project/fixtures/tests/funding_sources.json',
        'project/fixtures/tests/categories.json',
        'project/fixtures/tests/projects.json',
        'project/fixtures/tests/memberships.json',
        'system/fixtures/access_methods.json',
        'system/fixtures/applications.json',
        'system/fixtures/systems.json',
        'system/fixtures/os.json',
        'system/fixtures/hardware_groups.json',
        'system/fixtures/partitions.json',
    ]

    def test_required_command_line_args(self):
        '''
        Ensure an error is displayed to the user if the required command line
        args are not supplied.
        '''
        with self.assertRaises(CommandError) as e:
            out = StringIO()
            call_command('import_daily_compute', stdout=out)
        self.assertIn(
            'Error: the following arguments are required: -f/--file, -d, -m, -y, -s',
            str(e.exception),
        )

    def test_invalid_statsfile_path(self):
        '''
        Ensure an error is displayed to the user if the path to the stats file
        is invalid.
        '''
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=invalid_statsfile.out',
            '-d 31',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        self.assertIn('invalid_statsfile.out not found', out.getvalue())

    def test_invalid_day_value(self):
        '''
        Ensure an error is displayed to the user if the day value is invalid.
        '''
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=/app/stats/tests/hawk_10_2020.out',
            '-d 99',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        self.assertIn('day is out of range for month', out.getvalue())

    def test_invalid_month_value(self):
        '''
        Ensure an error is displayed to the user if the month value is invalid.
        '''
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=/app/stats/tests/hawk_10_2020.out',
            '-d 31',
            '-m 99',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        self.assertIn('month must be in 1..12', out.getvalue())

    def test_invalid_year_value(self):
        '''
        Ensure an error is displayed to the user if the year value is invalid.
        '''
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=/app/stats/tests/hawk_10_2020.out',
            '-d 31',
            '-m 10',
            '-y -1',
            '-s CF',
            stdout=out,
        )
        self.assertIn('year -1 is out of range', out.getvalue())

    def test_invalid_system_code(self):
        '''
        Ensure an error is displayed to the user if the system code is invalid.
        '''
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=/app/stats/tests/hawk_10_2020.out',
            '-d 31',
            '-m 10',
            '-y 2020',
            '-s INVALID',
            stdout=out,
        )
        self.assertIn("System 'INVALID' not found", out.getvalue())

    def test_valid_statsfile_for_31_10_2020(self):
        '''
        Ensure the stats file for 31/10/2020 is processed correclty.
        '''
        self.assertEqual(ComputeDaily.objects.count(), 0)
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=/app/stats/tests/hawk_10_2020.out',
            '-d 31',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )

        # Checkout output
        self.assertIn('INFO: Parsed array size 5 jobs', out.getvalue())
        self.assertIn(
            'INFO: Added new: 1 2020-10-31 00:00:00 Aaron Owen (issa16@cardiff.ac.uk) scw1124 CF-htc Default SSH 20 5 days, 5:44:24 0:00:10 0:10:20 5',
            out.getvalue()
        )
        self.assertIn('END - 1 new records, 0 updated records', out.getvalue())

        # Check database
        self.assertEqual(ComputeDaily.objects.count(), 1)
        record = ComputeDaily.objects.get()
        self.assertEqual(str(record.date), '2020-10-31')
        self.assertEqual(record.number_jobs, 5)
        self.assertEqual(record.number_processors, 20)
        self.assertEqual(str(record.user), 'Aaron Owen (issa16@cardiff.ac.uk)')
        self.assertEqual(record.project.code, 'scw1124')
        self.assertEqual(record.partition.name, 'CF-htc')
        self.assertEqual(record.application.name, 'Default')
        self.assertEqual(record.access_method.name, 'SSH')
        self.assertEqual(str(record.wait_time), '5 days, 5:44:24')
        self.assertEqual(str(record.cpu_time), '0:00:10')
        self.assertEqual(str(record.wall_time), '0:10:20')

    def test_valid_statsfile_for_02_10_2020(self):
        '''
        Ensure the stats file for 02/10/2020 is processed correclty.
        '''
        self.assertEqual(ComputeDaily.objects.count(), 0)
        out = StringIO()
        call_command(
            'import_daily_compute',
            '-f=/app/stats/tests/hawk_10_2020.out',
            '-d 02',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        # Checkout output
        self.assertIn('INFO: Parsed array size 10 jobs', out.getvalue())
        self.assertIn(
            'Added new: 1 2020-10-02 00:00:00 Aaron Owen (issa16@cardiff.ac.uk) scw1124 CF-htc Default SSH 1 0:00:20 29 days, 22:12:35 30 days, 0:01:50 10',
            out.getvalue()
        )
        self.assertIn('END - 1 new records, 0 updated records', out.getvalue())

        # Check database
        self.assertEqual(ComputeDaily.objects.count(), 1)
        record = ComputeDaily.objects.get()
        self.assertEqual(str(record.date), '2020-10-02')
        self.assertEqual(record.number_jobs, 10)
        self.assertEqual(record.number_processors, 1)
        self.assertEqual(str(record.user), 'Aaron Owen (issa16@cardiff.ac.uk)')
        self.assertEqual(record.project.code, 'scw1124')
        self.assertEqual(record.partition.name, 'CF-htc')
        self.assertEqual(record.application.name, 'Default')
        self.assertEqual(record.access_method.name, 'SSH')
        self.assertEqual(str(record.wait_time), '0:00:20')
        self.assertEqual(str(record.cpu_time), '29 days, 22:12:35')
        self.assertEqual(str(record.wall_time), '30 days, 0:01:50')
