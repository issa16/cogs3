import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from project.models import Project
from project.models import ProjectUserMembership


@receiver(post_save, sender=Project)
def update_project(sender, instance, created, **kwargs):
    if not created:
        project = instance
        if (project.status == Project.APPROVED):
            # Create or update a ProjectUserMembership instance for the project's technical lead.
            ProjectUserMembership.objects.update_or_create(
                project=project,
                user=project.tech_lead,
                defaults={
                    'date_joined': datetime.date.today(),
                    'status': ProjectUserMembership.AUTHORISED,
                },
            )
