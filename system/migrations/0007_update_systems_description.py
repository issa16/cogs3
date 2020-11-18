from django.db import migrations


def update_systems_description(apps, schema_editor):
    System = apps.get_model('system', 'System')

    hawk = System.objects.get(name='Hawk')
    hawk.description = 'Deployment of Dell Skylake nodes at CF'
    hawk.save()

    sunbird = System.objects.get(name='Sunbird')
    sunbird.description = 'Deployment of Dell Skylake nodes at SW'
    sunbird.save()


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_auto_20201118_2253'),
    ]

    operations = [
        migrations.RunPython(update_systems_description),
    ]