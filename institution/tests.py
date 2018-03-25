from django.test import TestCase

from .models import Institution


class InstitutionTests(TestCase):

    def create_institution(self):
        return Institution.objects.create(
            name='Bangor University',
            base_domain='bangor.ac.uk',
        )

    def test_institution_creation(self):
        institution = self.create_institution()
        self.assertTrue(isinstance(institution, Institution))
        self.assertEqual(institution.__str__(), institution.name)
