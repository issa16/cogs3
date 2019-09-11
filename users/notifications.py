from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django_rq import job

from institution.models import Institution
from common.util import email_user


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
