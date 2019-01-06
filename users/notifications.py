from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django_rq import job

from institution.models import Institution


def email_user(subject, context, text_template_path, html_template_path):
    """
    Dispatch a notification email.

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


@job
def user_created_notification(user):
    """
    Notify support that a user has created an account. 
    """
    subject = _('{company_name} User Account Created'.format(company_name=settings.COMPANY_NAME))
    support_email = Institution.parse_support_email_from_user_email(user.email)
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'university': user.profile.institution.name,
        'reason': user.reason_for_account,
        'to': support_email,
    }
    text_template_path = 'notifications/user/created.txt'
    html_template_path = 'notifications/user/created.html'
    email_user(subject, context, text_template_path, html_template_path)
