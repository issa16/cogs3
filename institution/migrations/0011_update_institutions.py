from django.db import migrations


def update_institutions(apps, schema_editor):
    Institution = apps.get_model('institution', 'Institution')

    # Aber
    obj, _ = Institution.objects.get_or_create(base_domain='aber.ac.uk')
    obj.name = 'Aberystwyth University'
    obj.identity_provider = 'https://shibboleth.aber.ac.uk/shibboleth'
    obj.academic = True
    obj.commercial = False
    obj.service_provider = True
    obj.logo_path = '/static/img/aberystwyth_logo.png'
    obj.save()

    # Bangor
    obj, _ = Institution.objects.get_or_create(base_domain='bangor.ac.uk')
    obj.name = 'Bangor University'
    obj.identity_provider = 'https://idp.bangor.ac.uk/shibboleth'
    obj.academic = True
    obj.commercial = False
    obj.service_provider = True
    obj.logo_path = '/static/img/bangor_logo.svg'
    obj.save()

    # Cardiff
    obj, _ = Institution.objects.get_or_create(base_domain='cardiff.ac.uk')
    obj.name = 'Cardiff University'
    obj.identity_provider = 'https://idp.cardiff.ac.uk/shibboleth'
    obj.academic = True
    obj.commercial = False
    obj.service_provider = True
    obj.logo_path = '/static/img/cardiff_logo.svg'
    obj.save()

    # Swansea
    obj, _ = Institution.objects.get_or_create(base_domain='swan.ac.uk')
    obj.name = 'Swansea University'
    obj.identity_provider = 'https://iss-openathensla-runtime.swan.ac.uk/oala/metadata'
    obj.academic = True
    obj.commercial = False
    obj.service_provider = True
    obj.logo_path = '/static/img/swansea_logo.png'
    obj.save()

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