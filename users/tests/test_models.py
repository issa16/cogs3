from django.contrib.auth.models import Group
from django.test import TestCase

from institution.models import Institution
from users.admin import CustomUserAdmin
from users.models import CustomUser
from users.models import Profile
from users.models import ShibbolethProfile


class CustomUserTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')

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
    def create_shibboleth_user(cls, email):
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

    def verify_user_data(self, user):
        self.assertTrue(isinstance(user, CustomUser))
        user_str = '{first_name} {last_name} ({email})'.format(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
        self.assertEqual(user.__str__(), user_str)
        self.assertEqual(user.get_full_name(), user.email)
        self.assertEqual(user.get_short_name(), user.email)
        self.assertEqual(user.username, user.email)

    def test_shibboleth_user_creation(self):
        """
        Ensure a shibboleth custom user is created correctly.
        """
        username = 'joe.bloggs'
        email = '@'.join([username, self.institution.base_domain])
        user = self.create_shibboleth_user(email=email)

        # User
        self.verify_user_data(user)
        self.assertTrue(user.is_shibboleth_login_required)

        # Profile
        profile = user.profile
        self.assertTrue(isinstance(profile, ShibbolethProfile))
        self.assertEqual(CustomUserAdmin.get_scw_username(user), profile.scw_username)
        self.assertEqual(CustomUserAdmin.get_account_status(user), profile.get_account_status_display())
        self.assertEqual(profile.shibboleth_id, email)
        self.assertEqual(profile.institution, self.institution)
        self.assertEqual(profile.department, '')
        self.assertEqual(profile.orcid, '')
        self.assertEqual(profile.scopus, '')
        self.assertEqual(profile.homepage, '')
        self.assertEqual(profile.cronfa, '')

    def test_non_shibboleth_user_creation(self):
        """
        Ensure a non shibboleth custom user is created correctly.
        """
        email = '@'.join(['joe.bloggs', self.institution.base_domain])
        user = self.create_non_shibboleth_user(email=email)

        # User
        self.verify_user_data(user)
        self.assertFalse(user.is_shibboleth_login_required)

        # Profile
        profile = user.profile
        self.assertTrue(isinstance(profile, Profile))
        self.assertEqual(CustomUserAdmin.get_scw_username(user), profile.scw_username)
        self.assertEqual(CustomUserAdmin.get_account_status(user), profile.get_account_status_display())
        self.assertEqual(profile.scw_username, '')
        self.assertEqual(profile.hpcw_username, '')
        self.assertEqual(profile.hpcw_email, '')
        self.assertEqual(profile.description, '')
        self.assertEqual(profile.phone, '')
        self.assertEqual(profile.account_status, Profile.AWAITING_APPROVAL)
