# Generated by Django 2.0.2 on 2018-08-21 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0014_institution_rse_notify_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='local_mailing_list_link',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='local_mailing_list_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]