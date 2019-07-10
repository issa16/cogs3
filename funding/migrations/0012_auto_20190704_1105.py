# Generated by Django 2.2.2 on 2019-07-04 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0011_auto_20180831_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='associated_to',
            field=models.CharField(default=None, editable=False, max_length=20),
        ),
        migrations.AddField(
            model_name='historicalattribution',
            name='associated_to',
            field=models.CharField(default=None, editable=False, max_length=20),
        ),
        migrations.AddField(
            model_name='historicalfundingsource',
            name='associated_to',
            field=models.CharField(default=None, editable=False, max_length=20),
        ),
        migrations.AddField(
            model_name='historicalpublication',
            name='associated_to',
            field=models.CharField(default=None, editable=False, max_length=20),
        ),
    ]
