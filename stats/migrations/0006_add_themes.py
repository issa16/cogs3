from django.db import migrations


def add_themes(apps, schema_editor):
    Theme = apps.get_model('stats', 'Theme')

    themes = [
        'Default',
        'Trial Projects',
        'Skills Academy',
        'Multi Sector',
        'Life Sciences',
        'ICT',
        'Genomics',
        'Financial Modelling',
        'Extra Accounting',
        'Energy & Environment',
        'Creative Industries',
        'Construction',
        'Chemistry',
        'Adv. Mat. & Man.',
    ]

    for theme in themes:
        record, created = Theme.objects.get_or_create(name=theme,)
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_add_8280_cores'),
    ]

    operations = [
        migrations.RunPython(add_themes),
    ]
