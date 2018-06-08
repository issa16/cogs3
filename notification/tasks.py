import abc
import django_rq
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template

logger = logging.getLogger('queue')


class EmailTask(abc.ABC):

    @property
    @abc.abstractmethod
    def email(self):
        return


class QueuedTask(abc.ABC):

    @abc.abstractmethod
    def enqueue(self):
        return


class QueuedEmailTask(QueuedTask, EmailTask):

    def __init__(self, email_context, template_context=None):
        super(QueuedEmailTask, self).__init__()
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

    def _send_email(self):
        try:
            self.email.send(fail_silently=False)
        except Exception:
            logger.exception('Failed to send email')

    def enqueue(self):
        django_rq.enqueue(self._send_email)
