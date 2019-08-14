import os
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings

import numpy as np
import pandas as pd

from project.models import Project
from priority.models import SlurmPriority

# remove false postive warning about chained assignment the default is 'warn'
pd.options.mode.chained_assignment = None


def read_raw_sacct_dump(filename):
    df = pd.read_csv(filename, sep='|')

    # remove NANs
    df = df.dropna(how='any')

    # only include complete jobs, not job-steps
    df = df[df.JobID.str.match('[0-9]+$')]

    # remove root from accounts list
    indexroot = df[df['Account'] == 'root'].index
    df.drop(indexroot, inplace=True)

    # convert cpu time from core seconds to core hours
    df['CPUTimeHours'] = df['CPUTimeRAW'].div(3600)

    return df


def read_and_aggregate_sacct_dump(filename):
    df = read_raw_sacct_dump(filename)

    # separate into gpu and not gpu
    gpu_data = df[(df.Partition == "gpu") | (df.Partition == "xgpu")]
    compute_data = df[(df.Partition != "gpu") & (df.Partition != "xgpu")]

    # calculate the total raw cpu time used for each project
    cpu_total_time = (compute_data.groupby('Account')['CPUTimeHours']
                      .sum()
                      .astype(int)
                      .to_frame(name='cpu_total_time'))
    gpu_total_time = (gpu_data.groupby('Account')['CPUTimeHours']
                      .sum()
                      .astype(int)
                      .to_frame(name='gpu_total_time'))

    return cpu_total_time, gpu_total_time


def calculate_priority(priority_attribution_data, sacct_data):
    # number of QOS levels
    QOS_levels = 4.0

    # combine the three data frames into one
    cpu_total_time, gpu_total_time = sacct_data
    full_data = (
        priority_attribution_data
        .rename(columns={'account': 'Account'})
        .merge(cpu_total_time, on='Account', how='outer')
        .merge(gpu_total_time, on='Account', how='outer')
        .fillna(0)
        .rename(columns={'Account': 'account'})
    )

    # Added to avoid problems in the event that projects are in the sacct
    # Dump but not on Cogs (e.g. Cardiff users temporarily using Sunbird).
    # These would otherwise default to an AP of Zero which crashes the
    # np.log10 function.
    full_data.attribution_points.loc[
        full_data.attribution_points == 0
    ] = 50000

    # Calculate cpu/gpu hours used since last sacct dump.
    full_data['cpu_hours_delta'] = (full_data['cpu_total_time']
                                    - full_data['cpu_hours_to_date'])
    full_data['gpu_hours_delta'] = (full_data['gpu_total_time']
                                    - full_data['gpu_hours_to_date'])

    # Calculate parameter such that K*log(AP) has a max defined by
    # QOS_levels
    max_AP = full_data['attribution_points'].max()
    k = QOS_levels / np.log10(max_AP)

    # Check if previous run was prioritised and if so add the time since
    # last sacct dump to total priortised time
    prioritised_projects = full_data[full_data['quality_of_service'] > 0]
    prioritised_projects['prioritised_cpu_hours'] += (
        prioritised_projects['cpu_hours_delta']
    )
    prioritised_projects['prioritised_gpu_hours'] += (
        prioritised_projects['gpu_hours_delta']
    )
    full_data.update(prioritised_projects)

    full_data['cpu_hours_to_date'] = full_data['cpu_total_time']
    full_data['gpu_hours_to_date'] = full_data['gpu_total_time']

    # Calculate Priority
    full_data['AP_credit'] = (
        (
            full_data['attribution_points']
            - (
                full_data['prioritised_cpu_hours']
                * full_data['AP_per_CPU_hour']
                + full_data['prioritised_gpu_hours']
                * full_data['AP_per_GPU_hour']
            )
        )
        .astype(int)
    )

    full_data['quality_of_service'] = (
        full_data['attribution_points']
        .map(lambda a: k * np.log10(a))
        .round(0)
        .astype(int))
    full_data['quality_of_service'] = (
        full_data['quality_of_service'].where(
            full_data['AP_credit'] >= 0, 0
        )
    )
    return full_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-i',
            '--input_file',
            help='Path to `sacct` dump file. This can be an absolute path, or '
            'relative to the Django base directory. If this is not specfied, '
            'the default path is "priority/IO/TEST_dump.csv".',
            default='priority/IO/TEST_dump.csv'
        )
        parser.add_argument(
            '-o',
            '--output_file',
            help='Path to output file where the priority values will be '
            'stored. This can be an absolute path, or relative to the '
            'Django base directory. If this is not specfied, '
            'the default path is "priority/IO/QOS_output.csv".',
            default='priority/IO/QOS_output.csv'
        )

    def handle(self, *args, **options):
        in_path = options['input_file']
        if os.path.isabs(in_path):
            in_path = os.path.join(settings.BASE_DIR, in_path)
        out_path = options['output_file']
        if os.path.isabs(out_path):
            out_path = os.path.join(settings.BASE_DIR, out_path)

        sacct_data = read_and_aggregate_sacct_dump(in_path)
        priority_attribution_data = get_priority_attribution_data()
        priority_results = calculate_priority(priority_attribution_data,
                                              sacct_data)

        # output Acount and QOS to pipe seperated csv file
        priority_results.to_csv(
            out_path,
            sep='|',
            columns=['account', 'quality_of_service'],
            index=False
        )

        for project_record in priority_results.itertuples():
            update_SlurmPriority_and_Project_tables(project_record)


def update_SlurmPriority_and_Project_tables(project_record,
                                            override_date=None):
    '''
    Accepts a Pandas NamedTuple containing at least project `account`,
    current `attribution_points` total, current `quality_of_service`,
    then `cpu_hours_to_date`,
    `gpu_hours_to_date`, `prioritised_cpu_hours`, and `prioritised_gpu_hours`,
    and writes these to the relevant points in the SlurmPriority and
    Project tables.
    `override_date` allows a different date to be provided for testing
    purposes.
    '''
    # Write current AP and QOS to Project table
    Project.objects.filter(
        code=project_record.account
    ).update(
        active_attribution_points=project_record.attribution_points,
        quality_of_service=project_record.quality_of_service
    )

    # Write history to the SlurmPriority table
    if override_date:
        today = override_date
    else:
        today = date.today()

    try:
        project_object = Project.objects.get(code=project_record.account)
    except Project.DoesNotExist:
        project_object = None

    SlurmPriority.objects.update_or_create(
        date=today,
        account=project_record.account,
        project=project_object,
        defaults={
            'attribution_points': project_record.attribution_points,
            'cpu_hours_to_date': project_record.cpu_hours_to_date,
            'gpu_hours_to_date': project_record.gpu_hours_to_date,
            'prioritised_cpu_hours': project_record.prioritised_cpu_hours,
            'prioritised_gpu_hours': project_record.prioritised_gpu_hours,
            'quality_of_service': project_record.quality_of_service
        }
    )


def get_priority_attribution_data():
    '''
    Counts the attribution points for all projects in the Cogs3 database,
    and then joins this to the stored totals for these objects in the
    database (should these exist) for comparison.
    '''

    attribution_points = [(project.code, project.AP())
                          for project in Project.objects.all()]
    attribution_data = pd.DataFrame(attribution_points,
                                    columns=['account', 'attribution_points'])
    yesterday = date.today() - timedelta(1)
    priority_db = SlurmPriority.objects.filter(date=yesterday)

    # If Priority DB exists merge in the AP values
    if priority_db.exists():
        priority_data = pd.DataFrame(
            list(
                priority_db.values(
                    'account',
                    'cpu_hours_to_date',
                    'gpu_hours_to_date',
                    'prioritised_cpu_hours',
                    'prioritised_gpu_hours',
                    'quality_of_service'
                )
            )
        )
        priority_attribution_data = pd.merge(
            priority_data,
            attribution_data,
            on='account',
            how='outer').fillna(0)
    else:
        # Priority DB is empty therfore create default values for projects that
        # are prioritized. These will then be added into the database during
        # the final append step.
        zeros = np.zeros(len(attribution_data))
        priority_attribution_data = attribution_data.copy()
        priority_attribution_data['cpu_hours_to_date'] = zeros
        priority_attribution_data['gpu_hours_to_date'] = zeros
        priority_attribution_data['prioritised_cpu_hours'] = zeros
        priority_attribution_data['prioritised_gpu_hours'] = zeros
        priority_attribution_data['quality_of_service'] = zeros

    # Add in institutional weights
    project_institution_db = Project.objects.select_related(
        'tech_lead__profile__shibbolethprofile__institution'
    )
    project_institution_data = pd.DataFrame(list(project_institution_db.values(
        'code',
        'tech_lead__profile__shibbolethprofile__institution__AP_per_GPU_hour',
        'tech_lead__profile__shibbolethprofile__institution__AP_per_CPU_hour'
    )))
    project_institution_data = project_institution_data.rename(columns={
        'tech_lead__profile__shibbolethprofile__institution__AP_per_GPU_hour':
        'AP_per_GPU_hour',
        'tech_lead__profile__shibbolethprofile__institution__AP_per_CPU_hour':
        'AP_per_CPU_hour'
    })

    priority_attribution_data = (
        pd
        .merge(priority_attribution_data,
               project_institution_data,
               left_on='account',
               right_on='code',
               how='inner')
        .fillna(0)
        .drop(columns='code')
    )

    return priority_attribution_data
