from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from institution.tests import InstitutionTests
from users.models import CustomUser


class CustomUserTests(TestCase):

    def setUp(self):
        self.base_domain = 'bangor.ac.uk'
        InstitutionTests().create_institution(
            name='Bangor University',
            base_domain=self.base_domain,
        )

    def create_custom_user(self, username, password, group):
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=username,
            first_name='Joe',
            last_name='Bloggs',
        )
        user.groups.add(group)
        return user

    def create_research_software_engineer_user(self, username, password):
        research_software_engineer_group = Group.objects.get(name='research_software_engineer')
        user = self.create_custom_user(
            username=username,
            password=password,
            group=research_software_engineer_group,
        )
        return user

    def create_student_user(self, username, password):
        student_group = Group.objects.get(name='student')
        user = self.create_custom_user(
            username=username,
            password=password,
            group=student_group,
        )
        return user

    def create_techlead_user(self, username, password):
        technical_lead_group = Group.objects.get(name='technical_lead')
        user = self.create_custom_user(
            username=username,
            password=password,
            group=technical_lead_group,
        )
        return user

    def test_research_software_engineer_user_creation(self):
        username = 'scw_research_software_engineer@' + self.base_domain
        user = self.create_research_software_engineer_user(username=username, password='123456')
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
        self.assertEqual(user.profile.__str__(), username)

    def test_techlead_user_creation(self):
        username = 'scw_techlead@' + self.base_domain
        user = self.create_techlead_user(username=username, password='123456')
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
        self.assertEqual(user.profile.__str__(), username)

    def test_student_user_creation(self):
        username = 'scw_student@' + self.base_domain
        user = self.create_student_user(username=username, password='123456')
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
        self.assertEqual(user.profile.__str__(), username)
