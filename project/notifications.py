from django.conf import settings
from django.core.mail import EmailMessage

from notification.tasks import EmailNotification
from notification.tasks import enqueue_email


class ProfileEmailNotification(EmailNotification):

    def __init__(self, profile):
        super(ProfileEmailNotification, self).__init__()
        self.profile = profile

        # Parse the profile details...

    def send(self):
        enqueue_email(self.email)


class ProjectUserMembershipEmailNotification(EmailNotification):

    def __init__(self, project_user_membership):
        super(ProjectUserMembershipEmailNotification, self).__init__()
        self.project_user_membership = project_user_membership

        # Parse the project user membership details...

    def send(self):
        enqueue_email(self.email)


class ProjectEmailNotification(EmailNotification):

    def __init__(self, project):
        super(ProjectEmailNotification, self).__init__()
        self.project = project

        # Parse project details...
        subject = ''
        body = ''
        to = self.project.tech_lead

        self.email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [to],
            [settings.DEFAULT_BCC_EMAIL],
        )

    def send(self):
        enqueue_email(self.email)
