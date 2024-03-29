from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_rq import job

from institution.models import Institution
from users.notifications import email_user


@job
def project_created_notification(project):
    """
    Notify support that a new project has been created.
    """
    subject = _('{company_name} Project Created'.format(company_name=settings.COMPANY_NAME))
    support_email = Institution.parse_support_email_from_user_email(project.tech_lead.email)
    context = {
        'code': project.code,
        'university': project.tech_lead.profile.institution.name,
        'technical_lead': project.tech_lead,
        'title': project.title,
        'to': support_email,
    }
    text_template_path = 'notifications/project/created.txt'
    html_template_path = 'notifications/project/created.html'
    email_user(subject, context, text_template_path, html_template_path)


@job
def project_membership_created(membership):
    """
    Notify the project's technical lead that a project membership has been created.
    """
    subject = _('{company_name} Project Membership Request'.format(company_name=settings.COMPANY_NAME))
    context = {
        'code': membership.project.code,
        'tech_lead_first_name': membership.project.tech_lead.first_name,
        'applicant_first_name': membership.user.first_name,
        'applicant_last_name': membership.user.last_name,
        'applicant_university': membership.user.profile.institution.name,
        'to': membership.project.tech_lead.email,
    }
    text_template_path = 'notifications/project_membership/created.txt'
    html_template_path = 'notifications/project_membership/created.html'
    email_user(subject, context, text_template_path, html_template_path)
