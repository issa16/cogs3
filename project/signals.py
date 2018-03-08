import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project
from .models import ProjectUserMembership


@receiver(post_save, sender=Project)
def update_project_membership(sender, instance, created, **kwargs):
    if not created:
        # If the project has been set to approved, create or update a ProjectUserMembership entry for the tech lead
        project = instance
        if (project.status == Project.APPROVED):
            obj, created = ProjectUserMembership.objects.update_or_create(
                project=project,
                user=project.tech_lead,
                defaults={
                    'date_joined': datetime.date.today(),
                    'status': ProjectUserMembership.AUTHORISED,
                },
            )
