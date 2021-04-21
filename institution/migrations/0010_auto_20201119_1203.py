# Generated by Django 2.2.13 on 2020-11-19 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0009_institution_support_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='academic',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='institution',
            name='commercial',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='institution',
            name='service_provider',
            field=models.BooleanField(default=False),
        ),
    ]
