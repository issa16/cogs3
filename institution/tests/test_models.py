from django.test import TestCase

from institution.exceptions import InvalidInstitutionalEmailAddress
from institution.exceptions import InvalidInstitutionalIndentityProvider
from institution.models import Institution


class InstitutionTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/institutions.json',
    ]

    def test_valid_institutional_email_address(self):
        self.assertTrue(Institution.is_valid_email_address('user@example.ac.uk'))

    def test_invalid_institutional_email_address(self):
        with self.assertRaises(InvalidInstitutionalEmailAddress) as e:
            Institution.is_valid_email_address('invalid-email@invalid.ac.uk')
        self.assertEqual(str(e.exception), 'Email address domain is not supported.')

    def test_valid_institutional_identity_provider(self):
        self.assertTrue(Institution.is_valid_identity_provider('https://idp.example.ac.uk/shibboleth'))

    def test_invalid_institutional_identity_provider(self):
        with self.assertRaises(InvalidInstitutionalIndentityProvider) as e:
            Institution.is_valid_identity_provider('https://idp.invalid-identity-provider.ac.uk/shibboleth')
        self.assertEqual(str(e.exception), 'Identity provider is not supported.')

    def test_id_str_produced(self):
        institution = Institution.objects.get(name='Example University')
        self.assertEqual(institution.id_str(), "example-university")
