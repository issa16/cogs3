from django.test import TestCase

from .models import Institution


class InstitutionTests(TestCase):

    def create_institution(self, name, base_domain):
        return Institution.objects.create(
            name=name,
            base_domain=base_domain,
        )

    def test_institution_creation(self):
        institution = self.create_institution(
            name='Bangor University',
            base_domain='bangor.ac.uk',
        )
        self.assertTrue(isinstance(institution, Institution))
        self.assertEqual(institution.__str__(), institution.name)
