import abc
import django_rq
import logging

from django.core.mail import EmailMessage

logger = logging.getLogger('queue')


def _send_email(email):
    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception('Failed to send email')


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

    def enqueue(self):
        django_rq.enqueue(_send_email, self.email)
