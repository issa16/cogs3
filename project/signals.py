from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group

from project.models import Project


@receiver(pre_delete, sender=Project)
def remove_tech_lead_from_project_owner(**kwargs):
    # If the tech lead has no other projects, remove them
    # from the project_owner group
    project = kwargs["instance"]
    tech_lead = project.tech_lead
    status = project.status
    techlead_projects = Project.objects.filter(
        tech_lead=tech_lead,
        status=Project.APPROVED,
    )
    if status == Project.APPROVED and techlead_projects.count() == 1:
        group = Group.objects.get(name='project_owner')
        tech_lead.groups.remove(group)
