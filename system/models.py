from django.db import models
from django.utils.translation import gettext_lazy as _


class Application(models.Model):
    """
    Represents an application.
    """

    class Meta:
        verbose_name_plural = _('Applications')

    name = models.CharField(max_length=128)
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


class System(models.Model):
    """
    Represents a System.
    """

    class Meta:
        verbose_name_plural = _('Systems')

    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512)
    number_of_cores = models.PositiveIntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OperatingSystem(models.Model):
    """
    Represents an operating system.
    """

    class Meta:
        verbose_name_plural = 'Operating Systems'

    name = models.CharField(max_length=128)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


class HardwareGroup(models.Model):
    """
    Represents a hardware group.
    """

    class Meta:
        verbose_name_plural = 'Hardware Groups'

    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512)
    total_number_of_cores = models.IntegerField()
    system = models.ForeignKey(
        System,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


class Partition(models.Model):
    """
    Represents a partition.
    """
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=512)
    hardware_group = models.ForeignKey(
        HardwareGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    os = models.ForeignKey(
        OperatingSystem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    cores_per_node = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    CORE = 0
    RESEARCH = 1
    PARTITION_TYPE_CHOICES = (
        (CORE, _('Core')),
        (RESEARCH, _('Research')),
    )
    partition_type = models.PositiveSmallIntegerField(
        choices=PARTITION_TYPE_CHOICES,
        default=CORE,
        verbose_name=_('Partition Type'),
    )

    def __str__(self):
        return f'{self.name}'
