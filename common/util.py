from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

import logging
import requests

class SubscriptionFailedError(Exception):
    pass


def email_user(subject, context, text_template_path, html_template_path):
    """
    Dispatch a notification email to a user.

    Args:
        subject (str): Email subject - required
        context (str): Email context - required
        text_template_path (str): text_template_path - required
        html_template_path (str): html_template_path - required
    """
    text_template = get_template(text_template_path)
    html_template = get_template(html_template_path)
    html_alternative = html_template.render(context)
    text_alternative = text_template.render(context)
    email = EmailMultiAlternatives(
        subject,
        text_alternative,
        settings.DEFAULT_FROM_EMAIL,
        [context['to']],
        bcc=[settings.DEFAULT_BCC_EMAIL],
    )
    email.attach_alternative(html_alternative, "text/html")
    email.send(fail_silently=False)


def mailing_list_subscribe(url, email):
    """
    Subscribe a user to a mailing list.

    Args:
        url: A URL that will subscribe a user to a mailing list, when the
             variable 'email' is replaced with an email address.

        email: The user's email address.
    """

    try:
        request = requests.get(url.format(email=email))
        if request.status_code < 200 or request.status_code >= 400:
            raise SubscriptionFailedError(
                "Server returned HTTP {}".format(request.status_code)
            )
    except Exception as ex:
        logger = logging.getLogger('apps')
        logger.exception(
            "Unable to subscribe %s to mailing list: %s", email, str(ex)
        )
