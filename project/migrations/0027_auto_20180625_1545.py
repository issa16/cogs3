# Generated by Django 2.0.2 on 2018-06-25 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0026_auto_20180625_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='pi_email',
            field=models.CharField(max_length=128, verbose_name='Principal Investigator Email'),
        ),
    ]
