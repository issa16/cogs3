from django.db import migrations


def set_partition_types(apps, schema_editor):
    Partition = apps.get_model('system', 'Partition')

    core_partitions = [
        'CF-compute',
        'CF-xcompute',
        'CF-compute64',
        'CF-compute64b',
        'CF-highmem',
        'CF-xhighmem',
        'CF-htc',
        'CF-xhtc',
        'CF-gpu',
        'CF-xgpu',
        'CF-dev',
        'CF-xdev',
        'CF-compute_amd',
        'CF-xcompute_amd',
        'CF-gpu_v100',
        'CF-xgpu_v100',
        'SW-compute',
        'SW-development',
        'SW-xcompute',
        'SW-compute64',
        'SW-compute64b',
        'SW-gpu',
        'SW-xgpu',
    ]

    print('-' * 80)
    print('Set Core partitions')
    print('-' * 80)
    for partition in core_partitions:
        print(f'{partition}.partition_type = Core')
        row = Partition.objects.get(name=partition)
        row.partition_type = 0  # Core
        row.save()

    research_partitions = [
        'CF-c_compute_chemy1',
        'CF-c_compute_chemy_webmo',
        'CF-c_compute_mdi1',
        'CF-c_gpu_comsc1',
        'CF-c_gpu_diri1',
        'CF-c_compute_ligo1',
        'CF-c_gpu_ligo1',
        'CF-c_vhighmem_dri1',
        'CF-c_highmem_dri1',
        'CF-c_compute_dri1',
        'CF-c_compute_neuro1',
        'CF-c_compute_neuro1_long',
        'CF-c_compute_neuro1_smrtlink',
        'CF-c_compute_chemy2',
        'CF-c_compute_wgp',
        'CF-c_compute_wgp1',
        'CF-c_compute_huygens',
        'CF-c_compute_ligo2',
        'CF-xexternal',
        'SW-s_compute_chem',
        'SW-s_compute_chem_rse',
        'SW-s_gpu_eng',
    ]

    print('-' * 80)
    print('Set Research partitions')
    print('-' * 80)
    for partition in research_partitions:
        print(f'{partition}.partition_type = Research')
        row = Partition.objects.get(name=partition)
        row.partition_type = 1  # Research
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0005_partition_partition_type'),
    ]

    operations = [
        migrations.RunPython(set_partition_types),
    ]
