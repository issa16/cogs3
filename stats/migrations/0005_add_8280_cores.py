from django.db import migrations


def add_number_of_processors(apps, schema_editor):
    NumberOfProcessors = apps.get_model('stats', 'NumberOfProcessors')

    for i in range(1, 8281):
        record = NumberOfProcessors(number=i)
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20201118_2253'),
    ]

    operations = [
        migrations.RunPython(add_number_of_processors),
    ]