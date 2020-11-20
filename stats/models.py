from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import Project
from users.models import CustomUser
from system.models import Partition
from system.models import System
from system.models import Application
from system.models import AccessMethod


class ComputeDaily(models.Model):
    """
    Represents the compute daily statistics.
    """

    class Meta:
        verbose_name_plural = _('Compute Daily')

    date = models.DateField()
    number_jobs = models.PositiveIntegerField()
    wait_time = models.DurationField()
    cpu_time = models.DurationField()
    wall_time = models.DurationField()
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    partition = models.ForeignKey(
        Partition,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    access_method = models.ForeignKey(
        AccessMethod,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.date}:{self.number_jobs}:{self.user}:{self.project}:{self.queue}:{self.application}:{self.access_method}:{self.wait_time}:{self.cpu_time}:{self.wall_time}'


class StorageWeekly(models.Model):
    """
    Represents the weekly storage statistics.
    """

    class Meta:
        verbose_name_plural = _('Storage Weekly')

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    date = models.DateField()
    system = models.ForeignKey(
        System,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    home_space_used = models.BigIntegerField()
    home_files_used = models.BigIntegerField()
    scratch_space_used = models.BigIntegerField()
    scratch_files_used = models.BigIntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.project}:{self.date}'
