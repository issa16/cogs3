# Generated by Django 2.2.13 on 2020-11-18 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20201118_2253'),
        ('system', '0005_auto_20201118_2249'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='systemtoinstitutionmap',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='systemtoinstitutionmap',
            name='institution',
        ),
        migrations.RemoveField(
            model_name='systemtoinstitutionmap',
            name='system',
        ),
        migrations.RemoveField(
            model_name='system',
            name='phase',
        ),
        migrations.DeleteModel(
            name='Phase',
        ),
        migrations.DeleteModel(
            name='SystemToInstitutionMap',
        ),
    ]