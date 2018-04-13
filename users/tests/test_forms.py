from django.test import TestCase

from institution.tests.test_models import InstitutionTests
from users.forms import CustomUserCreationForm
from users.models import CustomUser


class CustomUserCreationFormTests(TestCase):

    def setUp(self):
        self.base_domain = 'bangor.ac.uk'
        self.institution = InstitutionTests().create_institution(
            name='Bangor University',
            base_domain=self.base_domain,
        )

    def test_user_creation_form_with_valid_data(self):
        form = CustomUserCreationForm(data={
            'username': 'test_username@' + self.base_domain,
            'first_name': 'test_firstname',
            'last_name': 'test_lastname',
        })
        self.assertTrue(form.is_valid())

    def test_user_creation_form_without_required_fields(self):
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])

    def test_user_creation_form_generates_passwords_on_save(self):
        username = 'test_username@' + self.base_domain
        form = CustomUserCreationForm(data={
            'username': username,
            'first_name': 'test_firstname',
            'last_name': 'test_lastname',
        })
        self.assertTrue(form.is_valid())
        # Ensure the user has been created and a password has been generated for the account.
        self.assertEqual(CustomUser.objects.filter(username=username).count(), 0)
        form.save()
        self.assertEqual(CustomUser.objects.filter(username=username).count(), 1)
        self.assertIsNotNone(CustomUser.objects.get(username=username).password)
