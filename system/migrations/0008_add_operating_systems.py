from django.db import migrations


def add_operation_systems(apps, schema_editor):
    OperatingSystem = apps.get_model('system', 'OperatingSystem')

    record = OperatingSystem(name='RHEL 7')
    record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_update_systems_description'),
    ]

    operations = [
        migrations.RunPython(add_operation_systems),
    ]
