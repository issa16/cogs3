# Generated by Django 2.0.2 on 2018-05-14 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0006_auto_20180509_0858'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='institution',
            options={'ordering': ('name',)},
        ),
    ]
