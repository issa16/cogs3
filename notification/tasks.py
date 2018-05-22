import django_rq
import logging

from abc import ABCMeta
from abc import abstractmethod

from django.core.mail import EmailMessage

from notification.tasks import enqueue_email

logger = logging.getLogger('queue')

NOT_YET_IMPLEMENED = 'Not yet implemented.'


class EmailNotification(object):
    """
    Represents an email notification.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, email):
        raise NotImplementedError(NOT_YET_IMPLEMENED)


def send_email(email_message):
    """
    Send an email.

    Args:
        email_message (django.core.mail.EmailMessage): TODO
    """
    try:
        email.content_subtype = "html"
        email.send(fail_silently=False)
        logger.info('Sent and email to:', to, 'subject:', subject)
    except Exception as e:
        logger.exception('Failed to send an email to:', to, 'subject:', subject)


def enqueue_email(email_message):
    """
    Enqueue an email to the default django rq queue.

    Args:
        email_message (django.core.mail.EmailMessage): TODO
    """
    django_rq.enqueue(send_email, email_message)
