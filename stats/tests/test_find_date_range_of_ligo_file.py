from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class FindDateRangeOfLIGOFileTest(TestCase):

    def test_required_command_line_args(self):
        '''
        Ensure an error is displayed to the user if the required command line
        args are not supplied.
        '''
        with self.assertRaises(CommandError) as e:
            out = StringIO()
            call_command('find_date_range_of_ligo_file', stdout=out)
        self.assertIn(
            'Error: the following arguments are required: -f/--file',
            str(e.exception),
        )

    def test_invalid_logfile_path(self):
        '''
        Ensure an error is displayed to the user if the path to the LIGO
        log file is invalid.
        '''
        out = StringIO()
        call_command(
            'find_date_range_of_ligo_file',
            '-f=invalid_logfile.out',
            stdout=out,
        )
        self.assertIn('invalid_logfile.out not found', out.getvalue())

    def test_valid_logfile_path(self):
        '''
        Ensure the earliest date found in the LIGO log file is displayed
        to the user.
        '''
        out = StringIO()
        call_command(
            'find_date_range_of_ligo_file',
            '-f=/app/stats/tests/ligo_11_2020.out',
            stdout=out,
        )
        self.assertIn('Earliest: 2020-09-30 17:59:26', out.getvalue())
