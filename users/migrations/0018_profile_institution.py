# Generated by Django 2.1.4 on 2019-08-15 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0029_auto_20190802_1109'),
        ('users', '0017_auto_20190815_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='institution',
            field=models.ForeignKey(default=1, help_text='Institution user is based', on_delete=django.db.models.deletion.CASCADE, to='institution.Institution'),
            preserve_default=False,
        ),
    ]
