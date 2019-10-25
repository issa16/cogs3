import datetime
import pprint

import mock
from django import forms
from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.translation import activate

from institution.models import Institution
from openldap.tests.test_api import OpenLDAPBaseAPITests
from users.forms import (
    CustomUserChangeForm, CustomUserCreationForm, ProfileUpdateForm,
    RegisterForm
)
from users.models import CustomUser, Profile
from users.tests.test_models import CustomUserTests


class ProfileUpdateFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(
            email='shibboleth.user@example.ac.uk'
        )
        self.guest_user = CustomUser.objects.get(
            email='guest.user@external.ac.uk'
        )

    @mock.patch('requests.post')
    def test_profile_activation(self, post_mock):
        """
        Ensure the profile update form works for institutional and external
        users when activating a user's account.
        """
        mail.outbox = []  # Clear mail outbox

        user = CustomUserTests.create_custom_user(
            email='activation-test@example.ac.uk',
            is_shibboleth_login_required=True
        )
        description = 'Test User'
        account_status = Profile.APPROVED
        form = ProfileUpdateForm(
            data={
                'user': user.pk,
                'scw_username': None,
                'description': description,
                'account_status': account_status,
            },
            instance=user.profile,
        )
        self.assertTrue(form.is_valid())

        # Mock the LDAP API post request
        jwt = (
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL29wZ'
            'W5sZGFwLmV4YW1wbGUuY29tLyIsImF1ZCI6Imh0dHBzOi8vb3BlbmxkYXAuZX'
            'hhbXBsZS5jb20vIiwiaWF0IjoxNTI3MTAwMTQxLCJuYmYiOjE1MjcwOTk1NDE'
            'sImRhdGEiOnsiY24iOiJlLmpvZS5ibG9nZ3MiLCJzbiI6IkJsb2dncyIsImdp'
            'ZE51bWJlciI6IjUwMDAwMDEiLCJnaXZlbm5hbWUiOiJKb2UiLCJkaXNwbGF5T'
            'mFtZSI6Ik1yIEpvZSBCbG9nZ3MiLCJ0aXRsZSI6Ik1yIiwiaG9tZWRpcmVjdG'
            '9yeSI6Ii9ob21lL2Uuam9lLmJsb2dncyIsImxvZ2luc2hlbGwiOiIvYmluL2J'
            'hc2giLCJvYmplY3RjbGFzcyI6WyJpbmV0T3JnUGVyc29uIiwicG9zaXhBY2Nv'
            'dW50IiwidG9wIl0sInRlbGVwaG9uZW51bWJlciI6IjAwMDAwLTAwMC0wMDAiL'
            'CJtYWlsIjoiYWN0aXZhdGlvbi10ZXN0QGV4YW1wbGUuYWMudWsiLCJ1aWQiOi'
            'JlLmpvZS5ibG9nZ3MiLCJ1aWRudW1iZXIiOiI1MDAwMDAxIn19.d_KDASWxtR'
            'z6rBbgaHWqpR-XvUtdl22BB9QNYUz2-Ko'
        )
        post_mock.return_value = OpenLDAPBaseAPITests.mock_response(
            self, status=201, content=jwt.encode()
        )
        form.save()  # Trigger LDAP API call

        self.assertEqual(user.profile.scw_username, 'e.joe.bloggs')
        self.assertEqual(user.profile.uid_number, '5000001')
        self.assertEqual(user.profile.description, description)
        self.assertEqual(user.profile.account_status, account_status)

        # Ensure account status change was propagated to LDAP
        call_args, call_kwargs = post_mock.call_args_list[0]
        call_url = call_args[0]
        expected_call_url = f'{settings.OPENLDAP_HOST}user/'
        self.assertEqual(call_url, expected_call_url)
        expected_call_kwargs = {
            'data': {
                'department': '',
                'email': 'activation-test@example.ac.uk',
                'firstName': 'Joe',
                'surname': 'Bloggs',
            },
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            },
            'timeout': 5
        }
        self.assertEqual(call_kwargs, expected_call_kwargs)

        # Ensure the user was notified of the change in account status
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertNotEqual(email.subject.find('Account Created'), -1)
        self.assertNotEqual(email.body.find('User Account Update'), -1)
        self.assertNotEqual(email.body.find(user.first_name), -1)

        # Clear call list
        post_mock.call_args_list = []

    @mock.patch('requests.delete')
    def test_profile_deactivation(self, delete_mock):
        """
        Ensure the profile update form works for institutional and external
        users when deactivating a user's account.
        """
        users = [self.shibboleth_user, self.guest_user]
        for user in users:
            mail.outbox = []  # Clear mail outbox

            scw_username = 'scw_username'
            uid_number = 5000001
            description = 'Test User'
            account_status = Profile.SUSPENDED
            form = ProfileUpdateForm(
                data={
                    'user': user.pk,
                    'scw_username': scw_username,
                    'uid_number': uid_number,
                    'description': description,
                    'account_status': account_status,
                },
                instance=user.profile,
            )
            self.assertTrue(form.is_valid())

            # Mock the LDAP API delete request
            delete_mock.return_value = OpenLDAPBaseAPITests.mock_response(
                self, status=204
            )
            form.save()  # Trigger the LDAP API call

            self.assertEqual(user.profile.scw_username, scw_username)
            self.assertEqual(user.profile.uid_number, uid_number)
            self.assertEqual(user.profile.description, description)
            self.assertEqual(user.profile.account_status, account_status)

            # Ensure account status change was propagated to LDAP
            call_args, call_kwargs = delete_mock.call_args_list[0]
            call_url = call_args[0]
            expected_call_url = f'{settings.OPENLDAP_HOST}user/{user.email}/'
            self.assertEqual(call_url, expected_call_url)
            expected_call_kwargs = {
                'headers': {
                    'Cache-Control': 'no-cache'
                },
                'timeout': 5
            }
            self.assertEqual(call_kwargs, expected_call_kwargs)

            # Ensure the user was notified of the change in account status
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.to, [user.email])
            self.assertNotEqual(email.subject.find('Account Deactivated'), -1)
            self.assertNotEqual(email.body.find('User Account Update'), -1)
            self.assertNotEqual(email.body.find(user.first_name), -1)

            # Clear call list
            delete_mock.call_args_list = []

    def test_pre_approved_options(self):
        """
        Ensure the correct account status options are available for accounts 
        that are awaiting approval.
        """
        self.shibboleth_user.profile.account_status = Profile.AWAITING_APPROVAL
        self.shibboleth_user.profile.save()
        self.assertEqual(
            self.shibboleth_user.profile.account_status,
            Profile.AWAITING_APPROVAL
        )

        form = ProfileUpdateForm(
            data={
                'user': self.shibboleth_user.pk,
                'account_status': self.shibboleth_user.profile.account_status,
            },
            instance=self.shibboleth_user.profile,
        )
        self.assertTrue(form.is_valid())
        form.save()

        expected_choices = Profile.PRE_APPROVED_OPTIONS
        actual_choices = form.fields['account_status'].widget.choices
        self.assertEqual(actual_choices, expected_choices)

    def test_post_approved_options(self):
        """
        Ensure the correct account status options are available for accounts 
        that have been approved.
        """
        self.shibboleth_user.profile.account_status = Profile.APPROVED
        self.shibboleth_user.profile.save()
        self.assertEqual(
            self.shibboleth_user.profile.account_status, Profile.APPROVED
        )

        form = ProfileUpdateForm(
            data={
                'user': self.shibboleth_user.pk,
                'account_status': Profile.APPROVED,
            },
            instance=self.shibboleth_user.profile,
        )
        self.assertTrue(form.is_valid())
        form.save()

        expected_choices = Profile.POST_APPROVED_OPTIONS
        actual_choices = form.fields['account_status'].widget.choices
        self.assertEqual(actual_choices, expected_choices)


@override_settings(DEFAULT_SUPPORT_EMAIL='admin_team@example.ac.uk')
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
        users = {
            '@'.join(['shibboleth.user', self.institution.base_domain]): True,
            'guest.user@external.ac.uk': False,
        }
        for email, shibboleth_required in users.items():
            data = {
                'email': email,
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'is_shibboleth_login_required': shibboleth_required,
            }
            form = CustomUserCreationForm(data=data)
            self.assertTrue(form.is_valid())
            form.save()

            # Ensure an email notification was created.
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(
                mail.outbox[0].subject,
                f'{settings.COMPANY_NAME} User Account Created'
            )
            self.assertIn(
                f"{data['first_name']} {data['last_name']}", mail.outbox[0].body
            )

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
            }
        )
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
        users = {
            '@'.join(['shibboleth.user', self.institution.base_domain]): True,
            'guest.user@external.ac.uk': False,
        }
        for email, shibboleth_required in users.items():
            form = CustomUserCreationForm(
                data={
                    'email': email,
                    'first_name': 'Joe',
                    'last_name': 'Bloggs',
                    'is_shibboleth_login_required': shibboleth_required,
                }
            )
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
            }
        )
        self.assertTrue(form.is_valid())

    def test_without_required_fields(self):
        """
        Ensure the registration form fails if the required fields are missing.
        """
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])
        self.assertEqual(
            form.errors['reason_for_account'], ['This field is required.']
        )
        self.assertEqual(
            form.errors['accepted_terms_and_conditions'],
            ['This field is required.']
        )


class CustomUserChangeFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.shibboleth_user = CustomUser.objects.get(
            email='shibboleth.user@example.ac.uk'
        )

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
