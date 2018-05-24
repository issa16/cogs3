from django.db import models

from institution.models import Institution


class System(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512)
    number_of_cores = models.PositiveIntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SystemToInstitutionMap(models.Model):
    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = 'System to Institution Mappings'
        unique_together = (('system', 'institution'), )
