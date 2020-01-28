from django import template

register = template.Library()

@register.filter
def project_can_be_viewed(project, user):
    try:
        return project.can_view_project(user)
    except Exception as e:
        False
        # Since templates (and therefore filters) cannot propagate exceptions, better to fail here
        False
        # Since templates (and therefore filters) cannot propagate exceptions, better to fail here
