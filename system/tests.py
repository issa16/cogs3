from django.test import TestCase

from .models import System


class SystemTests(TestCase):

    def create_system(self, name, description, number_of_cores):
        return System.objects.create(
            name=name,
            description=description,
            number_of_cores=number_of_cores,
        )

    def test_system_creation(self):
        system = self.create_system(
            name='Nemesis',
            description='Bangor University Cluster',
            number_of_cores=10000,
        )
        self.assertTrue(isinstance(system, System))
        self.assertEqual(system.__str__(), system.name)
