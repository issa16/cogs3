from django.db import models

from project.models import Project


class SlurmPriority(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    account = models.CharField(
        max_length=20,
        verbose_name=('Slurm account name'),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True
    )

    # New fields added for Prioritisation
    attribution_points = models.IntegerField(
        verbose_name=('Attribution Points (AP)'),
        default=50000,
        help_text=('Calculated Attribution Points for this project'),
    )
    cpu_hours_to_date = models.IntegerField(
        verbose_name=('Total CPU hours to date'),
        default=0,
        help_text=('CPU compute hours used since this project began'),
    )
    gpu_hours_to_date = models.IntegerField(
        verbose_name=('Total GPU hours to date'),
        default=0,
        help_text=('GPU compute hours used since this project began'),
    )
    prioritised_gpu_hours = models.IntegerField(
        verbose_name=('Prioritised GPU hours'),
        default=0,
        help_text=('Total GPU compute hours in a prioritised state since '
                   'this project began'),
    )
    prioritised_cpu_hours = models.IntegerField(
        verbose_name=('Prioritised CPU hours'),
        default=0,
        help_text=('Total CPU compute hours in a prioritised state since '
                   'this project began'),
    )
    quality_of_service = models.IntegerField(
        verbose_name=('Quality of Service (QOS)'),
        help_text=('Quality of service value for this project, to be '
                   'provided to Slurm.'),
        default=0,
    )
