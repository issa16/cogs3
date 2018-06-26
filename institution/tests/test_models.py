from django.test import TestCase

from institution.exceptions import InvalidIndentityProvider
from institution.exceptions import InvalidInstitution
from institution.models import Institution


class InstitutionTests(TestCase):

    fixtures = [
        'institution/fixtures/tests/mock_institutions.yaml',
    ]

    @classmethod
    def create_institution(cls, name, base_domain, identity_provider):
        """
        Create an Institution instance.

        Args:
            name (str): Name of the institution.
            base_domain (str): Base domain of the institution.
            identity_provider (str): Institution's Shibboleth identity provider.
        """
        return Institution.objects.create(
            name=name,
            base_domain=base_domain,
            identity_provider=identity_provider,
        )

    def test_institution_creation(self):
        """
        Ensure we can create an Institution instance.
        """
        name = 'Test University'
        base_domain = 'test-example.ac.uk'
        identity_provider = 'https://idp.test-example.ac.uk/shibboleth'
        institution = self.create_institution(
            name=name,
            base_domain=base_domain,
            identity_provider=identity_provider,
        )
        self.assertTrue(isinstance(institution, Institution))
        self.assertEqual(institution.__str__(), institution.name)
        self.assertEqual(institution.name, name)
        self.assertEqual(institution.base_domain, base_domain)
        self.assertEqual(institution.identity_provider, identity_provider)

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
