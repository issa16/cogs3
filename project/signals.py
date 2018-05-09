import datetime
import logging

from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from project.models import Project
from project.models import ProjectUserMembership

logger = logging.getLogger('apps')


@receiver(post_save, sender=Project)
def update_project(sender, instance, created, **kwargs):
    if not created:
        try:
            project = instance
            if (project.status == Project.APPROVED):
                # Update or create a ProjectUserMembership instance for the project's technical lead.
                ProjectUserMembership.objects.update_or_create(
                    project=project,
                    user=project.tech_lead,
                    defaults={
                        'date_joined': datetime.date.today(),
                        'status': ProjectUserMembership.AUTHORISED,
                    },
                )

                # Assign the 'project_owner' group to the project's technical lead.
                group = Group.objects.get(name='project_owner')
                project.tech_lead.groups.add(group)
        except Exception:
            logger.exception(
                'Failed to update or create a ProjectUserMembership instance for the project\'s technical lead.')
