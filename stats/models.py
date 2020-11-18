from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import Project
from users.models import CustomUser
from system.models import Queue
from system.models import System


class Application(models.Model):
    """
    Represents an application.
    """

    name = models.CharField(max_length=128)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


class Theme(models.Model):
    """
    Represents a theme.
    """
    name = models.CharField(max_length=128, unique=True)
    distinguished_name = models.CharField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


class AccessMethod(models.Model):
    """
    Represents an access method.
    """

    class Meta:
        verbose_name_plural = _('Access Methods')

    name = models.CharField(max_length=64)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


class NumberOfProcessors(models.Model):
    """
    Represents the number of processors.
    """

    class Meta:
        verbose_name_plural = _('Number Of Processors')

    number = models.IntegerField(unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.number}'


class DailyStat(models.Model):
    """
    Represents the daily statistics.
    """

    class Meta:
        verbose_name_plural = _('Daily Stats')

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
    queue = models.ForeignKey(
        Queue,
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
    number_of_processors = models.ForeignKey(
        NumberOfProcessors,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.date}:{self.number_jobs}:{self.user}:{self.project}:{self.queue}:{self.application}:{self.access_method}:{self.wait_time}:{self.cpu_time}:{self.wall_time}'


class WeeklyStatStorageProjectsCF(models.Model):
    """
    Represents the weekly project storage statistics.
    """

    class Meta:
        verbose_name_plural = _('Weekly Stats Storage Projects CF')

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
