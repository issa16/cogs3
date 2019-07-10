# Generated by Django 2.2.2 on 2019-07-02 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0061_auto_20190702_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='attributions',
            field=models.ForeignKey(blank=True, default=None, limit_choices_to=models.Q(attributions=None), on_delete=django.db.models.deletion.CASCADE, to='funding.Attribution'),
        ),
    ]
