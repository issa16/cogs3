from django import template

register = template.Library()

@register.filter
def project_can_be_viewed(project, user):
    try:
        return project.can_view_project(user)
    except Exception as e:
        False
        # Since templates (and therefore filters) cannot propagate exceptions, better to fail here

@register.filter
def can_request_rse_allocation(project, user):
    try:
        return project.can_request_rse_allocation(user)
    except Exception as e:
        False
        # Since templates (and therefore filters) cannot propagate exceptions, better to fail here

@register.filter
def can_request_separate_supercomputer_usage(project, user):
    try:
        return project.can_request_separate_supercomputer_usage(user)
    except Exception as e:
        False
        # Since templates (and therefore filters) cannot propagate exceptions, better to fail here
