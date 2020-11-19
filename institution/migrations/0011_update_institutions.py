from django.db import migrations


def update_institutions(apps, schema_editor):
    Institution = apps.get_model('institution', 'Institution')

    # Update institution
    base_domains = [
        'aber.ac.uk',
        'bangor.ac.uk',
        'cardiff.ac.uk',
        'swan.ac.uk',
    ]
    for base_domain in base_domains:
        record = Institution.objects.get(base_domain=base_domain)
        record.academic = True
        record.commercial = False
        record.service_provider = True
        record.save()

    # Create LIGO institution
    ligo = Institution(
        name='LIGO',
        academic=True,
        commercial=False,
        service_provider=True,
    )
    ligo.save()

    # Create SCW institution
    scw = Institution(
        name='SCW',
        academic=True,
        commercial=False,
        service_provider=True,
    )
    scw.save()

    # Create Guest institution
    guest = Institution(
        name='Guest',
        academic=True,
        commercial=True,
        service_provider=True,
    )
    guest.save()


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0010_auto_20201119_1203'),
    ]

    operations = [
        migrations.RunPython(update_institutions),
    ]