from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.test import TestCase

from institution.models import Institution
from institution.models import Institution
from users.admin import CustomUserAdmin
from users.models import CustomUser
from users.models import CustomUserManager
from users.models import Profile
from users.models import ShibbolethProfile


class ProfileTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        self.guest_user = CustomUser.objects.get(email='guest.user@external.ac.uk')

    def test_is_awaiting_approval_status(self):
        self.shibboleth_user.profile.account_status = Profile.AWAITING_APPROVAL
        self.assertTrue(self.shibboleth_user.profile.is_awaiting_approval())

    def test_is_approved_status(self):
        self.shibboleth_user.profile.account_status = Profile.APPROVED
        self.assertTrue(self.shibboleth_user.profile.is_approved())

    def test_is_declined_status(self):
        self.shibboleth_user.profile.account_status = Profile.DECLINED
        self.assertTrue(self.shibboleth_user.profile.is_declined())

    def test_is_revoked_status(self):
        self.shibboleth_user.profile.account_status = Profile.REVOKED
        self.assertTrue(self.shibboleth_user.profile.is_revoked())

    def test_is_suspended_status(self):
        self.shibboleth_user.profile.account_status = Profile.SUSPENDED
        self.assertTrue(self.shibboleth_user.profile.is_suspended())

    def test_is_closed_status(self):
        self.shibboleth_user.profile.account_status = Profile.CLOSED
        self.assertTrue(self.shibboleth_user.profile.is_closed())

    def test_get_pre_approved_account_status_choices(self):
        self.shibboleth_user.profile.account_status = Profile.AWAITING_APPROVAL
        expected_choices = Profile.PRE_APPROVED_OPTIONS
        actual_choices = self.shibboleth_user.profile.get_account_status_choices()
        self.assertEqual(actual_choices, expected_choices)

    def test_get_post_account_status_choices(self):
        self.shibboleth_user.profile.account_status = Profile.APPROVED
        expected_choices = Profile.POST_APPROVED_OPTIONS
        actual_choices = self.shibboleth_user.profile.get_account_status_choices()
        self.assertEqual(actual_choices, expected_choices)

    def test_institution_property_for_shibboleth_user(self):
        expected = self.institution
        actual = self.shibboleth_user.profile.institution
        self.assertEqual(actual, expected)

    def test_institution_property_for_guest_user(self):
        self.assertIsNone(self.guest_user.profile.institution)

    def test_reset_account_status(self):
        self.shibboleth_user.profile.previous_account_status = Profile.AWAITING_APPROVAL
        self.shibboleth_user.profile.account_status = Profile.APPROVED
        self.assertEqual(self.shibboleth_user.profile.previous_account_status, Profile.AWAITING_APPROVAL)
        self.assertEqual(self.shibboleth_user.profile.account_status, Profile.APPROVED)
        self.shibboleth_user.profile.reset_account_status()
        self.assertEqual(self.shibboleth_user.profile.account_status, Profile.AWAITING_APPROVAL)

    def test_str(self):
        expected = str(self.shibboleth_user.email)
        actual = str(self.shibboleth_user.profile)
        self.assertEqual(actual, expected)


class CustomUserManagerTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            email='@'.join(['test-user', self.institution.base_domain]),
            password=CustomUser.objects.make_random_password(length=30),
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_shibboleth_login_required)

    def test_email_is_set_validation_error(self):
        with self.assertRaises(ValueError) as e:
            user = CustomUser.objects.create_superuser(
                email=None,
                password=CustomUser.objects.make_random_password(length=30),
            )
        self.assertEqual(str(e.exception), 'The Email must be set.')

    def test_is_staff_validation_error(self):
        with self.assertRaises(ValueError) as e:
            user = CustomUser.objects.create_superuser(
                email='@'.join(['test-user', self.institution.base_domain]),
                password=CustomUser.objects.make_random_password(length=30),
                is_staff=False,
            )
        self.assertEqual(str(e.exception), 'Superuser must have is_staff=True.')

    def test_is_superuser_validation_error(self):
        with self.assertRaises(ValueError) as e:
            user = CustomUser.objects.create_superuser(
                email='@'.join(['test-user', self.institution.base_domain]),
                password=CustomUser.objects.make_random_password(length=30),
                is_superuser=False,
            )
        self.assertEqual(str(e.exception), 'Superuser must have is_superuser=True.')

    def test_is_shibboleth_login_required_validation_error(self):
        with self.assertRaises(ValueError) as e:
            user = CustomUser.objects.create_superuser(
                email='@'.join(['test-user', self.institution.base_domain]),
                password=CustomUser.objects.make_random_password(length=30),
                is_shibboleth_login_required=True,
            )
        self.assertEqual(str(e.exception), 'Superuser must have is_shibboleth_login_required=False.')


class CustomUserTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        self.guest_user = CustomUser.objects.get(email='guest.user@external.ac.uk')

    def test_get_full_name(self):
        expected = self.shibboleth_user.email
        actual = self.shibboleth_user.get_full_name()
        self.assertEqual(actual, expected)

    def test_get_short_name(self):
        expected = self.shibboleth_user.email
        actual = self.shibboleth_user.get_short_name()
        self.assertEqual(actual, expected)

    def test_save_for_user_accounts(self):
        user_accounts = [
            self.shibboleth_user,
            self.guest_user,
        ]
        for user in user_accounts:
            user.first_name = 'John'
            user.save()
            self.assertEqual(user.first_name, 'John')

    def test_save_guest_user(self):
        pass

    def test_str(self):
        data = {
            'first_name': self.shibboleth_user.first_name,
            'last_name': self.shibboleth_user.last_name,
            'email': self.shibboleth_user.email,
        }
        expected = '{first_name} {last_name} ({email})'.format(**data)
        actual = str(self.shibboleth_user)
        self.assertEqual(actual, expected)

    @classmethod
    def create_custom_user(cls, email, group=None, is_shibboleth_login_required=True):
        """
        Create a CustomUser instance.

        Args:
            email (str): Email address.
            group (django.contrib.auth.models.Group): Group.
            is_shibboleth_login_required (bool): Is this user required to authenicatie via an
                approved shibboleth identity provider?
        """
        user = CustomUser.objects.create(
            username=email,
            email=email,
            first_name='Joe',
            last_name='Bloggs',
            is_shibboleth_login_required=is_shibboleth_login_required,
        )
        if group:
            user.groups.add(group)
        return user

    @classmethod
    def create_shibboleth_user(cls, email, institution):
        """
        Create a CustomUser instance that requires authentication via shibboleth.

        Args:
            email (str): Email address.
        """
        return CustomUserTests.create_custom_user(
            email=email,
            is_shibboleth_login_required=True,
        )

    @classmethod
    def create_non_shibboleth_user(cls, email):
        """
        Create a CustomUser instance that does not require authentication via shibboleth.

        Args:
            email (str): Email address.
        """
        return CustomUserTests.create_custom_user(
            email=email,
            is_shibboleth_login_required=False,
        )

    @classmethod
    def create_institutional_users(cls):
        inst_all = Institution.objects.all()

        names = [i.base_domain.split('.')[0] for i in inst_all]
        users = {}

        for i in names:
            username = f'{i}_user'
            email = f'{i}@{i}.ac.uk'

            users[i] = CustomUserTests.create_custom_user(email=email)

            return (names, users)
