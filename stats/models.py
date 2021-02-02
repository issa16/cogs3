from django.db import models
from django.utils.translation import gettext_lazy as _
from system.models import AccessMethod, Application, Partition, System
from users.models import CustomUser


class ComputeDaily(models.Model):
    """
    Represents the compute daily statistics.
    """

    class Meta:
        verbose_name_plural = _('Compute Daily')
        get_latest_by = "date"

    date = models.DateField()
    number_jobs = models.PositiveIntegerField()
    number_processors = models.PositiveIntegerField(default=0)
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
        'project.Project',  # To avoid circular imports issue
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
    
    def _get_total_processors(self):
        return self.number_jobs * self.number_processors
    total_processors = property(_get_total_processors)
   
    def __str__(self):
        return f'{self.date}:{self.number_jobs}:{self.number_processors}:{self.user}:{self.project}:{self.partition}:{self.application}:{self.access_method}:{self.wait_time}:{self.cpu_time}:{self.wall_time}'


class StorageWeekly(models.Model):
    """
    Represents the weekly storage statistics.
    """

    class Meta:
        verbose_name_plural = _('Storage Weekly')
        get_latest_by = "date"

    project = models.ForeignKey(
        'project.Project',  # To avoid circular imports issue
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
