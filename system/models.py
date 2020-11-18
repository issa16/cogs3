from django.db import models


class System(models.Model):
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


class Queue(models.Model):
    """
    Represents a system queue.
    """
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=512)
    cluster = models.ForeignKey(
        System,
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

    def __str__(self):
        return f'{self.name}'
