# Generated by Django 2.2.2 on 2019-07-16 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('priority', '0002_auto_20190716_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slurm_priority',
            name='project_code',
            field=models.CharField(max_length=200, verbose_name='SCW Project code extracted from sacct dump'),
        ),
    ]