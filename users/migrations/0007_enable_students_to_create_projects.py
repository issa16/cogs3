from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.db import migrations
"""
Students may apply for a project. If the project application is approved, 
their account will be elevated to a technical lead account.
"""
groups = {
    'student': [
        'add_project',
    ],
}


def create_groups(apps, schema_editor):

    # Ensure all permissions for all apps have been created
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None

    for group, permissions in groups.items():
        g, created = Group.objects.get_or_create(name=group)
        for permission in Permission.objects.filter(codename__in=permissions):
            g.permissions.add(permission)


def remove_groups(apps, schema_editor):
    Group.objects.filter(name__in=list(groups.keys())).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20180411_1600'),
        ('project', '0001_initial'),
    ]

    operations = [migrations.RunPython(create_groups, remove_groups)]
