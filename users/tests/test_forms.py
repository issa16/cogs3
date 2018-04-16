from django.test import TestCase

from institution.exceptions import InvalidInstitution
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
        """
        Ensure the user creation form works with valid data.
        """
        form = CustomUserCreationForm(
            data={
                'username': 'test_username@' + self.base_domain,
                'first_name': 'test_firstname',
                'last_name': 'test_lastname',
            }, )
        self.assertTrue(form.is_valid())

    def test_user_creation_form_with_an_invalid_username(self):
        """
        Ensure an InvalidInstitution error is returned if a user tries to create an account
        with a username that does not contain a valid institution base domain.
        """
        form = CustomUserCreationForm(
            data={
                'username': 'test_username@invalid_base_domain.com',
                'first_name': 'test_firstname',
                'last_name': 'test_lastname',
            }, )
        with self.assertRaises(InvalidInstitution):
            form.save()

    def test_user_creation_form_without_required_fields(self):
        """
        Ensure a user account can not be created without the required form fields.
        """
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])

    def test_user_creation_form_generates_passwords_on_save(self):
        """
        Ensure a password is genereted upon user account creation.
        """
        username = 'test_username@' + self.base_domain
        form = CustomUserCreationForm(data={
            'username': username,
            'first_name': 'test_firstname',
            'last_name': 'test_lastname',
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(CustomUser.objects.filter(username=username).count(), 1)
        self.assertIsNotNone(CustomUser.objects.get(username=username).password)
