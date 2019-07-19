from django.db import models
from django.conf import settings
from project.models import Project
from funding.models import Attribution
class slurm_priority(models.Model):
    Date = models.DateField(auto_now=False,auto_now_add=False)
    Account = models.CharField(
        max_length=20,
        verbose_name=('SCW Project code extracted from sacct dump'),
        )
    # New fields added for Prioritisation
    Ap=models.IntegerField(
            verbose_name=('Attribution points (Ap)'),
            default=50000,
            help_text=('Calculated Attribution points for this project'),
            )
    CPU_hours=models.IntegerField(
            verbose_name=('Total Cpu hours'),
            default=0,
            help_text=('cpu comute hours used since this project began'),
            )
    GPU_hours=models.IntegerField(
            verbose_name=('Total Gpu hours'),
            default=0,
            help_text=('GPU compute hours used since this project began'),
            )
    P_GPU=models.IntegerField(
            verbose_name=('prioritized Gpu hours'),
            default=0,
            help_text=('Total GPU compute hours in a priortized state since this project began'),
            )
    P_CPU=models.IntegerField(
            verbose_name=('prioritized Cpu hours'),
            default=0,
            help_text=('Total CPU compute hours in a priortized state since this project began'),
            )   
    Qos = models.IntegerField(
            verbose_name=('Quality of Service (QOS)'),   
            help_text=('Quality of service value for this project, to be input into slurm.'),
            default=0,
            )

