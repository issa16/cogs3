# Generated by Django 2.2.2 on 2019-07-17 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('priority', '0007_auto_20190717_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='slurm_priority',
            name='CPU_hours',
            field=models.IntegerField(default=0, help_text='Calculated cpu hours used for this project', verbose_name='Cpu hours'),
        ),
    ]
