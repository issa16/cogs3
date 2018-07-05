from django.test import TestCase

from institution.exceptions import InvalidInstitutionalEmailAddress
from institution.exceptions import InvalidInstitutionalIndentityProvider
from institution.models import Institution


class InstitutionTests(TestCase):

    fixtures = [
        'institution/fixtures/institutions.json',
    ]

    def _check_institution_system(self, institution):
        inst_name = institution.base_domain.split('.')[0]
        iss = institution.is_sunbird
        ics = institution.is_hawk
        if inst_name in ['swan', 'aber']:
            self.assertTrue(iss)
            self.assertFalse(ics)
        elif inst_name in ['cardiff', 'bangor']:
            self.assertTrue(ics)
            self.assertFalse(iss)
        else:
            raise ValueError(f'Institution {inst_name} not recognised')

    def test_institutional_predicates(self):
        """
        Ensure institutional methods (e.g. is_swan, is_swan_system etc) return correct values
        """
        institutions = Institution.objects.all()
        for institution in institutions:
            for institution_predicate in institutions:
                cond = institution.id == institution_predicate.id
                inst_name = institution_predicate.base_domain.split('.')[0]
                property_name = f'is_{inst_name}'
                property_val = getattr(institution, property_name)
                self.assertEqual(cond, property_val)

            self._check_institution_system(institution)

    def test_invalid_institutional_system(self):
        with self.assertRaises(ValueError) as e:
            institution = Institution.objects.create(
                name='Example University',
                base_domain='example.ac.uk',
                identity_provider='https://idp.example.ac.uk/shibboleth',
                logo_path='/static/img/example-logo.png',
            )
            self._check_institution_system(institution)
        self.assertEqual(str(e.exception), 'Institution example not recognised')

    def test_valid_institutional_email_address(self):
        self.assertTrue(Institution.is_valid_email_address('user@bangor.ac.uk'))

    def test_invalid_institutional_email_address(self):
        with self.assertRaises(InvalidInstitutionalEmailAddress) as e:
            Institution.is_valid_email_address('invalid-email@invalid.ac.uk')
        self.assertEqual(str(e.exception), 'Email address domain is not supported.')

    def test_valid_institutional_identity_provider(self):
        self.assertTrue(Institution.is_valid_identity_provider('https://idp.bangor.ac.uk/shibboleth'))

    def test_invalid_institutional_identity_provider(self):
        with self.assertRaises(InvalidInstitutionalIndentityProvider) as e:
            Institution.is_valid_identity_provider('https://idp.invalid-identity-provider.ac.uk/shibboleth')
        self.assertEqual(str(e.exception), 'Identity provider is not supported.')

    def test_id_str_produced(self):
        institution = Institution.objects.create(
            name='example University',
            base_domain='example.ac.uk',
            identity_provider='https://example.ac.uk/shibboleth',
        )
        self.assertEqual(institution.id_str(), "example-university")
