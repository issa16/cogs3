from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from users.models import Profile, UserLastLogin


class ImportUserLastLoginTest(TestCase):

    fixtures = [
        'users/fixtures/tests/users.json',
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
            call_command('import_user_last_login', stdout=out)
        self.assertIn(
            'Error: the following arguments are required: -f/--file',
            str(e.exception),
        )

    def test_invalid_loginfile_path(self):
        '''
        Ensure an error is displayed to the user if the path to the login file
        is invalid.
        '''
        out = StringIO()
        call_command(
            'import_user_last_login',
            '-f=invalid_loginfile.csv',
            stdout=out,
        )
        self.assertIn('invalid_loginfile.csv not found', out.getvalue())

    def test_valid_loginfile_path(self):
        '''
        Ensure a login file is processed correctly.
        '''
        self.assertEqual(UserLastLogin.objects.count(), 0)
        out = StringIO()
        call_command(
            'import_user_last_login',
            '-f=/app/stats/tests/user_last_login.csv',
            stdout=out,
        )
        # Verify a record has been created in database
        self.assertEqual(UserLastLogin.objects.count(), 1)

        self.assertIn('Last Login Sync, running on', out.getvalue())
        self.assertIn(
            'Reading file /app/stats/tests/user_last_login.csv',
            out.getvalue(),
        )

        # c.issa16 - Should list a create entry first
        self.assertIn(
            'create c.issa16 1590620400 2020-05-28 00:00:00 cl1',
            out.getvalue(),
        )

        # b.issa17 - Should list a create entry second
        self.assertIn(
            'create b.issa17 1590620500 2020-05-28 00:00:00 cl2',
            out.getvalue(),
        )
        self.assertIn('Could not find user b.issa17', out.getvalue())

        # c.issa16 - Should list an update entry third as this user
        # already has a UserLastLogin record.
        self.assertIn(
            'update c.issa16 1590620600 2020-05-28 00:00:00 cl2',
            out.getvalue(),
        )

        # Verify latest details for user login are available in database
        profile = Profile.objects.get(scw_username__iexact='c.issa16')
        user = profile.user
        user_last_login = UserLastLogin.objects.get(user=user)
        self.assertEqual(
            str(user_last_login.last_login_time),
            '2020-05-27 23:00:00+00:00',
        )
        self.assertEqual(
            str(user_last_login.last_login_unix_time),
            '1590620600',
        )
        self.assertEqual(str(user_last_login.last_login_host), 'cl2')

        self.assertIn('END', out.getvalue())
