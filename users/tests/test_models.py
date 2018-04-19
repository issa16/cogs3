from django.contrib.auth.models import Group
from django.test import TestCase

from institution.tests.test_models import InstitutionTests
from users.admin import CustomUserAdmin
from users.models import CustomUser
from users.models import Profile


class CustomUserTests(TestCase):

    def setUp(self):
        self.institution_base_domain = 'bangor.ac.uk'
        InstitutionTests.create_institution(
            name='Bangor University',
            base_domain=self.institution_base_domain,
        )

    @classmethod
    def create_custom_user(cls, username, password, group):
        """
        Create a CustomUser instance.

        Args:
            username (str): Account username.
            password (str): Account password.
            group (django.contrib.auth.models.Group): Associate the account with this group.
        """
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=username,
            first_name='Joe',
            last_name='Bloggs',
        )
        user.profile.scw_username = 'joe.bloggs'
        user.groups.add(group)
        return user

    @classmethod
    def create_research_software_engineer_user(cls, username, password):
        """
        Create a CustomUser instance that is linked to the research_software_engineer group.

        Args:
            username (str): Account username.
            password (str): Account password.
        """
        research_software_engineer_group = Group.objects.get(name='research_software_engineer')
        return CustomUserTests.create_custom_user(
            username=username,
            password=password,
            group=research_software_engineer_group,
        )

    @classmethod
    def create_student_user(cls, username, password):
        """
        Create a CustomUser instance that is linked to the student group.

        Args:
            username (str): Account username.
            password (str): Account password.
        """
        student_group = Group.objects.get(name='student')
        return CustomUserTests.create_custom_user(
            username=username,
            password=password,
            group=student_group,
        )

    @classmethod
    def create_techlead_user(cls, username, password):
        """
        Create a CustomUser instance that is linked to the technical_lead group.

        Args:
            username (str): Account username.
            password (str): Account password.
        """
        technical_lead_group = Group.objects.get(name='technical_lead')
        return CustomUserTests.create_custom_user(
            username=username,
            password=password,
            group=technical_lead_group,
        )

    def test_custom_user_admin_profile(self):
        """
        Ensure the custom user admin profile returns the correct data.
        """
        user = self.create_student_user(
            username='scw_student@' + self.institution_base_domain,
            password='123456',
        )
        self.assertEqual(CustomUserAdmin.get_institution(user), user.profile.institution)
        self.assertEqual(CustomUserAdmin.get_scw_username(user), user.profile.scw_username)
        self.assertEqual(CustomUserAdmin.get_shibboleth_username(user), user.username)
        self.assertEqual(
            CustomUserAdmin.get_account_status(user),
            Profile.STATUS_CHOICES[Profile.AWAITING_APPROVAL - 1][1],
        )

    def test_research_software_engineer_user_creation(self):
        """
        Ensure we can create a CustomUser instance that is linked to the research_software_engineer group.
        """
        username = 'scw_research_software_engineer@' + self.institution_base_domain
        user = self.create_research_software_engineer_user(
            username=username,
            password='123456',
        )
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
        self.assertEqual(user.profile.__str__(), username)

    def test_techlead_user_creation(self):
        """
        Ensure we can create a CustomUser instance that is linked to the technical_lead group.
        """
        username = 'scw_techlead@' + self.institution_base_domain
        user = self.create_techlead_user(
            username=username,
            password='123456',
        )
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
        self.assertEqual(user.profile.__str__(), username)

    def test_student_user_creation(self):
        """
        Ensure we can create a CustomUser instance that is linked to the student group.
        """
        username = 'scw_student@' + self.institution_base_domain
        user = self.create_student_user(
            username=username,
            password='123456',
        )
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
        self.assertEqual(user.profile.__str__(), username)
