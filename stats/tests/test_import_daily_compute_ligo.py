from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from project.models import Project, ProjectUserMembership
from stats.models import ComputeDaily
from users.models import CustomUser


class ImportDailyComputeLIGOTest(TestCase):

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
        with self.assertRaises(CommandError) as e:
            out = StringIO()
            call_command('import_daily_compute_ligo', stdout=out)
        self.assertIn(
            'Error: the following arguments are required: -f/--file, -d, -m, -y, -s',
            str(e.exception),
        )

    def test_invalid_statsfile_path(self):
        out = StringIO()
        call_command(
            'import_daily_compute_ligo',
            '-f=invalid_statsfile.out',
            '-d 1',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        self.assertIn('invalid_statsfile.out not found', out.getvalue())

    def test_invalid_day_value(self):
        out = StringIO()
        call_command(
            'import_daily_compute_ligo',
            '-f=/app/stats/tests/ligo_11_2020.out',
            '-d 99',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        self.assertIn('day is out of range for month', out.getvalue())

    def test_invalid_month_value(self):
        out = StringIO()
        call_command(
            'import_daily_compute_ligo',
            '-f=/app/stats/tests/ligo_11_2020.out',
            '-d 1',
            '-m 99',
            '-y 2020',
            '-s CF',
            stdout=out,
        )
        self.assertIn('month must be in 1..12', out.getvalue())

    def test_invalid_year_value(self):
        out = StringIO()
        call_command(
            'import_daily_compute_ligo',
            '-f=/app/stats/tests/ligo_11_2020.out',
            '-d 1',
            '-m 10',
            '-y -1',
            '-s CF',
            stdout=out,
        )
        self.assertIn('year -1 is out of range', out.getvalue())

    def test_invalid_system_value(self):
        out = StringIO()
        call_command(
            'import_daily_compute_ligo',
            '-f=/app/stats/tests/ligo_11_2020.out',
            '-d 1',
            '-m 10',
            '-y 2020',
            '-s INVALID',
            stdout=out,
        )
        self.assertIn("System 'INVALID' not found", out.getvalue())

    def test_valid_statsfile_for_1_10_2020(self):
        out = StringIO()
        call_command(
            'import_daily_compute_ligo',
            '-f=/app/stats/tests/ligo_11_2020.out',
            '-d 1',
            '-m 10',
            '-y 2020',
            '-s CF',
            stdout=out,
        )

        # Checkout output
        print(out.getvalue())
        self.assertIn(
            "DailyStatsParserLigo started for 2020-10-01 00:00:00 file /app/stats/tests/ligo_11_2020.ou", out.getvalue()
        )
        self.assertIn("INFO: Parsed array size 30568 jobs", out.getvalue())
        self.assertIn("Successfully created user account and profile: aaron.owen@ligo.org", out.getvalue())
        self.assertIn("aaron.owen@ligo.org already exists", out.getvalue())
        self.assertIn("END - 2 new records, 0 updated records", out.getvalue())
        self.assertIn("SUM WALL TIME=594 days, 9:40:02", out.getvalue())
        self.assertIn("MAX WALL TIME=3840 days, 0:00:00", out.getvalue())

        # Check database
        self.assertEqual(ComputeDaily.objects.count(), 2)

        # Check a project membership record was created for user
        project_user_membership = ProjectUserMembership.objects.filter(
            project=Project.objects.get(code='scw1158'),
            user=CustomUser.objects.get(email='aaron.owen@ligo.org'),
        ).exists()
        self.assertTrue(project_user_membership)

        # Check first record
        record = ComputeDaily.objects.all().first()
        self.assertEqual(str(record.date), '2020-10-01')
        self.assertEqual(record.number_jobs, 29549)
        self.assertEqual(record.number_processors, 1)
        self.assertEqual(str(record.user), 'Aaron Owen (aaron.owen@ligo.org)')
        self.assertEqual(record.project.code, 'scw1158')
        self.assertEqual(record.partition.name, 'CF-c_compute_ligo1')
        self.assertEqual(record.application.name, 'cbc.grb.cohptfoffline')
        self.assertEqual(record.access_method.name, 'CONDOR')
        self.assertEqual(str(record.wait_time), '34 days, 12:40:37')
        self.assertEqual(str(record.cpu_time), '556 days, 16:47:56')
        self.assertEqual(str(record.wall_time), '567 days, 15:48:22')

        # Check second record
        record = ComputeDaily.objects.all().last()
        self.assertEqual(str(record.date), '2020-10-01')
        self.assertEqual(record.number_jobs, 1019)
        self.assertEqual(record.number_processors, 1)
        self.assertEqual(str(record.user), 'Aaron Owen (aaron.owen@ligo.org)')
        self.assertEqual(record.project.code, 'scw1158')
        self.assertEqual(record.partition.name, 'CF-c_compute_ligo2')
        self.assertEqual(record.application.name, 'cbc.grb.cohptfoffline')
        self.assertEqual(record.access_method.name, 'CONDOR')
        self.assertEqual(str(record.wait_time), '1 day, 0:59:33')
        self.assertEqual(str(record.cpu_time), '26 days, 9:06:36')
        self.assertEqual(str(record.wall_time), '26 days, 17:51:40')
