from django.test import TestCase
from django.utils.translation import activate
from django.urls import reverse

from institution.tests.test_models import InstitutionTests
from users.tests.test_models import CustomUserTests
from users.forms import CustomUserCreationForm, CustomUserPersonalInfoUpdateForm
from users.models import CustomUser


class CustomUserCreationFormTests(TestCase):

    def setUp(self):
        # Create an institution
        self.institution = InstitutionTests.create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
            identity_provider='https://idp.bangor.ac.uk/shibboleth',
        )

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


class CustomUserPersonalInfoUpdateFormTests(TestCase):

    def setUp(self):
        # Create an institution
        self.institution = InstitutionTests.create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
            identity_provider='https://idp.bangor.ac.uk/shibboleth',
        )

    def test_user_update_form(self):
        email = '@'.join(['joe.bloggs', self.institution.base_domain])
        user = CustomUserTests.create_custom_user(
            email=email,
            has_accepted_terms_and_conditions=True,
        )
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        data = {
            'first_name': 'test',
            'last_name': 'user',
        }
        # First get a page and login in through the middleware
        self.client.get(reverse('update-user'), **headers)
        # Now post
        self.client.post(reverse('update-user'), data, **headers)
        user = CustomUser.objects.get(email=email)
        assert user.first_name == 'test'
        assert user.last_name == 'user'

    def test_register_unregistered_user_form(self):
        email = '@'.join(['joe.bloggs', self.institution.base_domain])
        user = CustomUserTests.create_custom_user(
            email=email,
            has_accepted_terms_and_conditions=False,
        )
        headers = {
            'Shib-Identity-Provider': self.institution.identity_provider,
            'REMOTE_USER': email,
        }
        data = {
            'first_name': 'test',
            'last_name': 'user',
            'has_accepted_terms_and_conditions': True,
        }
        self.client.get(reverse('register-existing'), **headers)
        self.client.post(reverse('register-existing'), data, **headers)
        user = CustomUser.objects.get(email=email)
        assert user.first_name == 'test'
        assert user.last_name == 'user'
