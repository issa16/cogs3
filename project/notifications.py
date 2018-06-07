from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from notification.tasks import QueuedEmailTask


class EmailNotification(QueuedEmailTask):

    def __init__(self, email_context, template_context=None):
        super(EmailNotification, self).__init__()
        if template_context:
            self.template_context = template_context
        else:
            self.template_context = {
                'text_template': 'notifications/email_base.txt',
                'html_template': 'notifications/email_base.html',
            }
        self.email_context = email_context

    @property
    def email(self):
        text_template = get_template(self.template_context['text_template'])
        html_template = get_template(self.template_context['html_template'])
        html_alternative = html_template.render(self.email_context)
        text_alternative = text_template.render(self.email_context)
        email = EmailMultiAlternatives(
            self.email_context['subject'],
            text_alternative,
            settings.DEFAULT_FROM_EMAIL,
            [self.email_context['to']],
        )
        email.attach_alternative(html_alternative, "text/html")
        return email
