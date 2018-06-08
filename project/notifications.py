from django.conf import settings

from notification.tasks import QueuedEmailTask


class ProjectStatusUpdateEmail(QueuedEmailTask):

    def __init__(self, project):
        subject = '{company_name} Project ({project_code}) Status Update'.format(
            company_name=settings.COMPANY_NAME,
            project_code=project.code,
        )
        email_context = {
            'subject': subject,
            'to': project.tech_lead.email,
            'project': project,
        }
        template_context = {
            'text_template': 'notifications/project_status_update.txt',
            'html_template': 'notifications/project_status_update.html',
        }
        super(ProjectStatusUpdateEmail, self).__init__(email_context, template_context)


class ProjectMembershipUpdateEmail(QueuedEmailTask):
    pass
