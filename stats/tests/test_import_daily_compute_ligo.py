from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
'''
class ImportDailyComputeLIGOTest(TestCase):

    fixtures = [
        'system/fixtures/systems.json',
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
        print(out.getvalue())
        self.assertIn(
            'DailyStatsParserLigo started for 2020-10-01 00:00:00 file /app/stats/tests/ligo_11_2020.out',
            out.getvalue()
        )
        self.assertIn('INFO: Parsed array size 30568 jobs', out.getvalue())
'''
