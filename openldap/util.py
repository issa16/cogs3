from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from security.json_web_token import JSONWebToken


def decode_response(response):
    return JSONWebToken.decode(
        data=response.content.strip(),
        key=settings.OPENLDAP_JWT_KEY,
        audience=settings.OPENLDAP_JWT_AUDIENCE,
        algorithms=settings.OPENLDAP_JWT_ALGORITHM,
    )


def email_user(subject, context, text_template_path, html_template_path):
    """
    Reset user account status to Awaiting Approval.

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
    )
    email.attach_alternative(html_alternative, "text/html")
    email.send(fail_silently=False)
