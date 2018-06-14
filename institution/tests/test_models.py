from django.test import TestCase

from institution.models import Institution


class InstitutionTests(TestCase):
    fixtures = [
        'institution/fixtures/institutions.yaml',
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
        name = 'New University'
        base_domain = 'new.ac.uk'
        identity_provider = 'https://idp.new.ac.uk/shibboleth'
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
            name='New University',
            base_domain='new.ac.uk',
            identity_provider='https://new.ac.uk/shibboleth',
        )
        self.assertEqual(institution.id_str(), "new-university")


    def test_institutional_predicates(self):
        """
        Ensure institutional methods (e.g. is_swansea, is_swansea_system etc) return correct values
        """
        institutions = Institution.objects.all()

        # loop over institutions
        for institution in institutions:
            # loop over institutions predicates
            for institution_predicate in institutions:
                cond = institution.id == institution_predicate.id

                inst_name = institution_predicate.base_domain.split('.')[0]
                property_name = f'is_{inst_name}'
                property_val = getattr(institution, property_name)

                self.assertEqual(cond, property_val)

            # check institution system
            inst_name = institution.base_domain.split('.')[0]

            iss = institution.is_sunbird
            ics = institution.is_hawk

            if inst_name in ['swansea','aber']:
                self.assertTrue(iss)
                self.assertFalse(ics)
            elif inst_name in ['cardiff','bangor']:
                self.assertTrue(ics)
                self.assertFalse(iss)
            else:
                raise ValueError(f'Institution {inst_name} not recognised')

