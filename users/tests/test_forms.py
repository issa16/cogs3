from django.test import TestCase
from django.utils.translation import activate

from institution.models import Institution
from users.forms import CustomUserChangeForm
from users.forms import CustomUserCreationForm
from users.models import CustomUser


class CustomUserChangeFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
        'users/fixtures/tests/users.json',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')
        self.user = CustomUser.objects.get(email='joe.bloggs@example.ac.uk')


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
            '@'.join(['joe.bloggs', self.institution.base_domain]): True,
            'joe.bloggs@external.ac.uk': False,
        }
        for email, shibboleth_required in test_cases.items():
            form = CustomUserCreationForm(
                data={
                    'email': email,
                    'first_name': 'Joe',
                    'last_name': 'Bloggs',
                    'is_shibboleth_login_required': shibboleth_required,
                }, )
            self.assertTrue(form.is_valid())

    def test_invalid_institution_email(self):
        """
        Ensure an email address from an unsupported institution domain is caught via the
        CustomUserCreationForm, if the user is required to login via a shibboleth IDP.
        """
        form = CustomUserCreationForm(
            data={
                'email': 'joe.bloggs@invalid_base_domain.com',
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'is_shibboleth_login_required': True,
            }, )
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
            '@'.join(['joe.bloggs', self.institution.base_domain]): True,
            'joe.bloggs@external.ac.uk': False,
        }
        for email, shibboleth_required in test_cases.items():
            form = CustomUserCreationForm(
                data={
                    'email': email,
                    'first_name': 'Joe',
                    'last_name': 'Bloggs',
                    'is_shibboleth_login_required': shibboleth_required,
                }, )
            self.assertTrue(form.is_valid())
            form.save()
            self.assertEqual(CustomUser.objects.filter(email=email).count(), 1)
            self.assertIsNotNone(CustomUser.objects.get(email=email).password)
