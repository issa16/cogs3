from project import notifications
from django.test import TestCase
from django.conf import settings
from project.models import Project, ProjectUserMembership, ProjectCategory
from users.models import CustomUser
from django.core import mail


class ProjectNotificationTests(TestCase):

    fixtures = ['institution/fixtures/institutions.json']

    def setUp(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        self.user = CustomUser.objects.create(
            username='user@aber.ac.uk', email='user@aber.ac.uk'
        )
        self.user.save()
        self.user2 = CustomUser.objects.create(
            username='user2@aber.ac.uk', email='user2@aber.ac.uk'
        )
        self.user2.save()
        self.project = Project(
            title="Project title",
            description="Project description",
            tech_lead=self.user,
            #            category=ProjectCategory.objects.get(pk=1)
        )
        self.project.save()

        self.membership = ProjectUserMembership.objects.create(
            user=self.user2, project=self.project, date_joined='2019-07-31'
        )

        self.membership.save()

    def test_project_created_notification(self):
        notifications.project_created_notification(self.project)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"

    def test_project_membership_created(self):
        membership = ProjectUserMembership.objects.get(pk=1)
        notifications.project_membership_created(self.membership)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"
