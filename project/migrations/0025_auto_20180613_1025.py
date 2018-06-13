# Generated by Django 2.0.2 on 2018-06-13 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0024_project_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, max_length=1024, verbose_name='Project Description'),
        ),
        migrations.AlterField(
            model_name='project',
            name='institution_reference',
            field=models.CharField(blank=True, max_length=128, verbose_name='Owning institution project reference'),
        ),
        migrations.AlterField(
            model_name='project',
            name='requirements_gateways',
            field=models.TextField(blank=True, help_text='Web gateway or portal name and versions', max_length=512, verbose_name='Requirements gateways'),
        ),
        migrations.AlterField(
            model_name='project',
            name='requirements_onboarding',
            field=models.TextField(blank=True, max_length=512, verbose_name='Requirements onboarding'),
        ),
        migrations.AlterField(
            model_name='project',
            name='requirements_software',
            field=models.TextField(blank=True, help_text='Software name and versions', max_length=512, verbose_name='Requirements software'),
        ),
        migrations.AlterField(
            model_name='project',
            name='requirements_training',
            field=models.TextField(blank=True, max_length=512, verbose_name='Requirements training'),
        ),
        migrations.AlterField(
            model_name='projectsystemallocation',
            name='openldap_status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Inactive')], default=1, verbose_name='OpenLDAP status'),
        ),
    ]
