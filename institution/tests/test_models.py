from django.conf import settings
from django.test import TestCase, override_settings

from institution.exceptions import (InvalidInstitutionalEmailAddress,
                                    InvalidInstitutionalIndentityProvider)
from institution.models import Institution


class InstitutionTests(TestCase):

    fixtures = [
        'institution/fixtures/institutions.json',
    ]

    def _check_institution_system(self, institution):
        # This checks institution fixtures. A bit redundant and 
        # not flexible if we want to change the fixtures.
        institution_name = institution.base_domain.split('.')[0]
        # checking separate_allocation_requests
        separate_alloc = institution.separate_allocation_requests
        if institution_name in ['bangor', 'aber', 'cardiff']:
            self.assertFalse(separate_alloc)
        elif institution_name == 'swan':
            self.assertTrue(separate_alloc)
        else:
            raise ValueError(f'Institution {institution_name} not recognised')

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

    def test_str_representation(self):
        institution = Institution.objects.create(
            name='Example University',
            base_domain='example.ac.uk',
            identity_provider='https://example.ac.uk/shibboleth',
        )
        self.assertEqual(institution.id_str(), "example-university")
        self.assertEqual(institution.__str__(), "Example University")

    @override_settings(DEFAULT_SUPPORT_EMAIL='support@another-example.ac.uk')
    def test_parse_support_email_from_user_email(self):
        """
        Ensure the correct support email address is returned.
        """
        institution = Institution.objects.create(
            name='Example University',
            base_domain='example.ac.uk',
            support_email='support@example.ac.uk',
        )
        test_cases = {
            "user@example.ac.uk": institution.support_email,
            "user@another-example.ac.uk": settings.DEFAULT_SUPPORT_EMAIL
        }
        for user_email, support_email in test_cases.items():
            result = Institution.parse_support_email_from_user_email(user_email)
            self.assertEqual(result, support_email)
