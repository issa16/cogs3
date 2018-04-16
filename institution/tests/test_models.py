from django.test import TestCase

from institution.models import Institution


class InstitutionTests(TestCase):

    def create_institution(self, name, base_domain):
        """
        Create an Institution instance.

        Args:
            name (str): Name of the institution.
            base_domain (str): Base domain of the institution.
        """
        return Institution.objects.create(
            name=name,
            base_domain=base_domain,
        )

    def test_institution_creation(self):
        """
        Ensure we can create an Institution instance.
        """
        institution = self.create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
        )
        self.assertTrue(isinstance(institution, Institution))
        self.assertEqual(institution.__str__(), institution.name)
