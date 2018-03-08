from django.contrib.auth.models import Group
from django.test import TestCase

from .models import CustomUser


class CustomUserTests(TestCase):

    def create_custom_user(self, username, group):
        user = CustomUser.objects.create(
            username=username,
            password='123456',
        )
        user.groups.add(group)
        return user

    def create_student_user(self, username):
        student_group = Group.objects.get(name='student')
        user = self.create_custom_user(username=username, group=student_group)
        return user

    def create_techlead_user(self, username):
        technical_lead_group = Group.objects.get(name='technical_lead')
        user = self.create_custom_user(username=username, group=technical_lead_group)
        return user

    def test_student_user_creation(self):
        username = 'scw_student'
        user = self.create_student_user(username=username)
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)

    def test_techlead_user_creation(self):
        username = 'scw_techlead'
        user = self.create_techlead_user(username='scw_techlead')
        self.assertTrue(isinstance(user, CustomUser))
        self.assertEqual(user.__str__(), username)
