import datetime

from django import forms
from django.test import TestCase
from django.utils.translation import activate

from institution.models import Institution
from users.forms import CustomUserChangeForm
from users.forms import CustomUserCreationForm
from users.forms import ProfileUpdateForm
from users.forms import RegisterForm
from users.models import CustomUser
from users.models import Profile


class ProfileUpdateFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')
        self.guest_user = CustomUser.objects.get(email='guest.user@external.ac.uk')

    def test_profile_update(self):
        """
        Ensure the profile update form works for institutional and external users.
        """
        test_cases = [
            self.shibboleth_user,
            self.guest_user,
        ]
        for test_case in test_cases:
            scw_username = 'x.test.username'
            uid_number = 5000001
            description = 'test user'
            account_status = 1
            form = ProfileUpdateForm(
                data={
                    'user': test_case.pk,
                    'scw_username': scw_username,
                    'uid_number': uid_number,
                    'description': description,
                    'account_status': account_status,
                },
                instance=test_case.profile,
            )
            self.assertTrue(form.is_valid())
            form.save()

            self.assertEqual(test_case.profile.scw_username, scw_username)
            self.assertEqual(test_case.profile.uid_number, uid_number)
            self.assertEqual(test_case.profile.description, description)
            self.assertEqual(test_case.profile.account_status, account_status)

    def test_pre_approved_options(self):
        """
        Ensure the correct account status options are available for accounts that are awaiting 
        approval.
        """
        self.shibboleth_user.profile.account_status = Profile.AWAITING_APPROVAL
        self.shibboleth_user.profile.save()
        self.assertEqual(self.shibboleth_user.profile.account_status, Profile.AWAITING_APPROVAL)

        form = ProfileUpdateForm(
            data={
                'user': self.shibboleth_user.pk,
                'account_status': self.shibboleth_user.profile.account_status,
            },
            instance=self.shibboleth_user.profile,
        )
        self.assertTrue(form.is_valid())

        expected_choices = Profile.PRE_APPROVED_OPTIONS
        actual_choices = form.fields['account_status'].widget.choices
        self.assertEqual(actual_choices, expected_choices)

    def test_post_approved_options(self):
        """
        Ensure the correct account status options are available for accounts that have been 
        approved.
        """
        self.shibboleth_user.profile.account_status = Profile.APPROVED
        self.shibboleth_user.profile.save()
        self.assertEqual(self.shibboleth_user.profile.account_status, Profile.APPROVED)

        form = ProfileUpdateForm(
            data={
                'user': self.shibboleth_user.pk,
                'account_status': Profile.APPROVED,
            },
            instance=self.shibboleth_user.profile,
        )
        self.assertTrue(form.is_valid())

        expected_choices = Profile.POST_APPROVED_OPTIONS
        actual_choices = form.fields['account_status'].widget.choices
        self.assertEqual(actual_choices, expected_choices)


class CustomUserCreationFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')

    def test_create_user(self):
        """
        Ensure the user creation form works for institutional and external users.
        """
        test_cases = {
            '@'.join(['shibboleth.user', self.institution.base_domain]): True,
            'guest.user@external.ac.uk': False,
        }
        for email, shibboleth_required in test_cases.items():
            form = CustomUserCreationForm(
                data={
                    'email': email,
                    'first_name': 'Joe',
                    'last_name': 'Bloggs',
                    'is_shibboleth_login_required': shibboleth_required,
                })
            self.assertTrue(form.is_valid())

    def test_invalid_institutional_email(self):
        """
        Ensure an email address from an unsupported institution domain is caught via the
        CustomUserCreationForm, if the user is required to login via a shibboleth IDP.
        """
        form = CustomUserCreationForm(
            data={
                'email': 'joe.bloggs@invalid_base_domain.ac.uk',
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'is_shibboleth_login_required': True,
            })
        self.assertFalse(form.is_valid())

    def test_without_required_fields(self):
        """
        Ensure a CustomUser instance can not be created without the required form fields.
        """
        activate('en')
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['This field is required.'])
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])

    def test_password_generation(self):
        """
        Ensure a random password is genereted new user accounts.
        """
        test_cases = {
            '@'.join(['shibboleth.user', self.institution.base_domain]): True,
            'guest.user@external.ac.uk': False,
        }
        for email, shibboleth_required in test_cases.items():
            form = CustomUserCreationForm(
                data={
                    'email': email,
                    'first_name': 'Joe',
                    'last_name': 'Bloggs',
                    'is_shibboleth_login_required': shibboleth_required,
                })
            self.assertTrue(form.is_valid())
            form.save()

            self.assertEqual(CustomUser.objects.filter(email=email).count(), 1)
            self.assertIsNotNone(CustomUser.objects.get(email=email).password)


class RegisterFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def test_user_registration(self):
        """
        Ensure the registration form works for shibboleth users.
        """
        form = RegisterForm(
            data={
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'reason_for_account': 'HPC',
                'accepted_terms_and_conditions': True,
            })
        self.assertTrue(form.is_valid())

    def test_without_required_fields(self):
        """
        Ensure the registration form fails if the required fields are missing.
        """
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])
        self.assertEqual(form.errors['reason_for_account'], ['This field is required.'])
        self.assertEqual(form.errors['accepted_terms_and_conditions'], ['This field is required.'])


class CustomUserChangeFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(email='shibboleth.user@example.ac.uk')

    def test_user_update(self):
        """
        Ensure the user update form works.
        """
        first_name = 'John'
        last_name = 'Smith'
        email = 'john.smith@example.ac.uk'
        form = CustomUserChangeForm(
            data={
                'username': self.shibboleth_user.username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'is_shibboleth_login_required': True,
                'date_joined': datetime.date.today(),
            },
            instance=self.shibboleth_user,
        )
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(self.shibboleth_user.first_name, first_name)
        self.assertEqual(self.shibboleth_user.last_name, last_name)
        self.assertEqual(self.shibboleth_user.email, email)

    def test_invalid_institutional_email(self):
        """
        Ensure an email address from an unsupported institution domain is caught.
        """
        with self.assertRaises(Institution.DoesNotExist):
            form = CustomUserChangeForm(
                data={
                    'username': self.shibboleth_user.username,
                    'first_name': self.shibboleth_user.first_name,
                    'last_name': self.shibboleth_user.last_name,
                    'email': 'john.smith@invalid-domain.ac.uk',
                    'is_shibboleth_login_required': True,
                    'date_joined': datetime.date.today(),
                },
                instance=self.shibboleth_user,
            )
            self.assertTrue(form.is_valid())
            form.save()
