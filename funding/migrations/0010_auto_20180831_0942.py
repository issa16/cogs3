# Generated by Django 2.0.2 on 2018-08-31 09:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    FundingSource = apps.get_model('funding', 'FundingSource')
    Publication = apps.get_model('funding', 'Publication')

    for fs in FundingSource.objects.all():
        try:
            if fs.pi.profile.institution.needs_funding_approval:
                fs.owner = fs.pi
            else:
                fs.owner = fs.created_by
        except:
            fs.owner = fs.created_by
        fs.save()

    for p in Publication.objects.all():
        p.owner = p.created_by
        p.save()

def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('funding', '0009_auto_20180829_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='owner',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='historicalattribution',
            name='owner',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalfundingsource',
            name='owner',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalpublication',
            name='owner',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(forwards, backwards),
    ]
