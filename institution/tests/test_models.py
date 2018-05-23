from django.test import TestCase

from institution.models import Institution


class InstitutionTests(TestCase):

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
        name = 'Bangor University'
        base_domain = 'bangor.ac.uk'
        identity_provider = 'https://idp.bangor.ac.uk/shibboleth'
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

    def test_id_str_produced(self):
        institution = self.create_institution(
            name='Swansea University',
            base_domain='swansea.ac.uk',
            identity_provider='https://iss-openathensla-runtime.swan.ac.uk/oala/metadata',
        )
        self.assertEqual(institution.id_str(), "swansea-university")
