from project import notifications
from django.test import TestCase, override_settings
from django.conf import settings
from project.models import Project, ProjectUserMembership, ProjectCategory
from users.models import CustomUser
from django.core import mail


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_SUPPORT_EMAIL='admin_team@example.ac.uk'
)
class ProjectNotificationTests(TestCase):

    fixtures = ['institution/fixtures/institutions.json']

    def setUp(self):
        self.base_domain = 'aber.ac.uk'
        self.user = CustomUser.objects.create(
            username=f'user@{self.base_domain}',
            email=f'user@{self.base_domain}'
        )
        self.user.save()
        self.user2 = CustomUser.objects.create(
            username=f'user2@{self.base_domain}',
            email=f'user2@{self.base_domain}'
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
        notifications.project_created_notification(self.project)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"

        assert len(mail.outbox[0].to) == 1,\
                'Mail should be sent to  one recipient'
        assert mail.outbox[0].to[0] == settings.DEFAULT_SUPPORT_EMAIL,\
                f'Wrong recipient: {mail.outbox[0].to}'

    def test_project_created_notification_institution_email(self):
        from institution.models import Institution
        uni = Institution.objects.get(base_domain=self.base_domain)
        uni.support_email = f'support@{self.base_domain}'
        uni.save()

        notifications.project_created_notification(self.project)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"

        assert len(mail.outbox[0].to) == 1,\
                'Mail should be sent to  one recipient'
        assert mail.outbox[0].to[ 0 ] == uni.support_email, \
                f'Wrong recipient: {mail.outbox[0].to}'

    def test_project_membership_created(self):
        membership = ProjectUserMembership.objects.get(pk=1)
        notifications.project_membership_created(self.membership)
        assert len(mail.outbox) > 0, "An email must be sent"
        assert len(mail.outbox) == 1, "Only one email must be sent"
