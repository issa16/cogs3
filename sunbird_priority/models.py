from django.db import models

# Create your models here.
class slurm_priority(models.Model):
    Date = models.DateField(auto_now=False,auto_now_add=True)
    project_code = models.ForeignKey(
            'Project',
            on_delete=models.CASCADE,
            help_text=('Project that the calculated priorities are associated with'),
            )
    Priority_Level=models.IntegerField(
            verbose_name=('Priority Level'),
            default=0,
            help_text=('Calculated priority level for this project'),
            )
#def Calculate_Priority
