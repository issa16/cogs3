from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings

from project import notifications
from project.models import Project, ProjectCategory, ProjectUserMembership
from users.models import CustomUser


@override_settings(DEFAULT_SUPPORT_EMAIL='admin_team@example.ac.uk')
class ProjectNotificationTests(TestCase):

    fixtures = ['institution/fixtures/institutions.json']

    def setUp(self):
        self.base_domain = 'aber.ac.uk'
        self.user = CustomUser.objects.create(
            username='user@{}'.format(self.base_domain),
            email='user@{}'.format(self.base_domain)
        )
        self.user.save()
        self.user2 = CustomUser.objects.create(
            username='user2@{}'.format(self.base_domain),
            email='user2@{}'.format(self.base_domain)
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

    def test_project_created_notification_default_email(self):
        # update the institution support email to be empty
        institution = self.project.tech_lead.profile.institution
        institution.support_email = ""
        institution.save()

        # reload project
        self.project = Project.objects.get(id=self.project.id)

        notifications.project_created_notification(self.project)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"

        assert len(mail.outbox[0].to) == 1,\
                'Mail should be sent to  one recipient'
        assert mail.outbox[0].to[0] == settings.DEFAULT_SUPPORT_EMAIL,\
                'Wrong recipient: {}'.format(mail.outbox[0].to)

    def test_project_created_notification_institution_email(self):
        from institution.models import Institution
        uni = Institution.objects.get(base_domain=self.base_domain)
        uni.support_email = 'support@{}'.format(self.base_domain)
        uni.save()

        notifications.project_created_notification(self.project)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"

        assert len(mail.outbox[0].to) == 1,\
                'Mail should be sent to  one recipient'
        assert mail.outbox[0].to[ 0 ] == uni.support_email, \
                'Wrong recipient: {}'.format(mail.outbox[0].to)

    def test_project_membership_created(self):
        membership = ProjectUserMembership.objects.get(pk=1)
        previous_email = len(mail.outbox)
        notifications.project_membership_created(self.membership)
        assert len(mail.outbox) - previous_email > 0, "An email must be sent"
        assert len(mail.outbox) - previous_email == 1, "Only one email must be sent"
