from django.test import TestCase
from django.utils.translation import activate

from institution.models import Institution
from users.forms import CustomUserCreationForm
from users.models import CustomUser


class CustomUserCreationFormTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.yaml',
    ]

    def setUp(self):
        self.institution = Institution.objects.get(name='Example University')

    def test_create_shibboleth_user(self):
        """
        Ensure the user creation form works for a shibboleth user.
        """
        form = CustomUserCreationForm(
            data={
                'email': '@'.join(['joe.bloggs', self.institution.base_domain]),
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'is_shibboleth_login_required': True,
            }, )
        self.assertTrue(form.is_valid())

    def test_create_non_shibboleth_user(self):
        """
        Ensure the user creation form works for a non shibboleth user.
        """
        form = CustomUserCreationForm(
            data={
                'email': '@'.join(['joe.bloggs', self.institution.base_domain]),
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'is_shibboleth_login_required': False,
            }, )
        self.assertTrue(form.is_valid())

    def test_invalid_institution_email(self):
        """
        Ensure an email address from an unsupported institution domain is caught via the
        CustomUserCreationForm if the user is required to login via a shibboleth IDP.
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
        form = CustomUserCreationForm(data={})
        activate('en')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['This field is required.'])
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])

    def test_password_generation_for_shibboleth_user(self):
        """
        Ensure a random password is genereted for a shibboleth user.
        """
        email = '@'.join(['joe.bloggs', self.institution.base_domain])
        form = CustomUserCreationForm(
            data={
                'email': email,
                'first_name': 'Joe',
                'last_name': 'Bloggs',
                'is_shibboleth_login_required': True,
            }, )
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(CustomUser.objects.filter(email=email).count(), 1)
        self.assertIsNotNone(CustomUser.objects.get(email=email).password)
