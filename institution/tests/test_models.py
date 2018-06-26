from django.test import TestCase

from institution.exceptions import InvalidIndentityProvider
from institution.exceptions import InvalidInstitution
from institution.models import Institution


class InstitutionTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.yaml',
    ]

    def test_valid_email_address(self):
        self.assertTrue(Institution.is_valid_email_address('user@example.ac.uk'))

    def test_invalid_email_address(self):
        with self.assertRaises(InvalidInstitution):
            Institution.is_valid_email_address('invalid-email')

    def test_valid_identity_provider(self):
        self.assertTrue(Institution.is_valid_identity_provider('https://idp.example.ac.uk/shibboleth'))

    def test_invalid_identity_provider(self):
        with self.assertRaises(InvalidIndentityProvider):
            Institution.is_valid_identity_provider('invalid-identity-provider')

    def test_id_str_produced(self):
        institution = Institution.objects.get(name='Example University')
        self.assertEqual(institution.id_str(), "example-university")
