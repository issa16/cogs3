import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import models
from sqlalchemy import create_engine, Table, update
import numpy as np
import pandas as pd
from datetime import date, timedelta
from project.models import Project, ProjectSystemAllocation
from funding.models import Attribution
from priority.models import slurm_priority
import sys
import os
from cogs3.settings import BASE_DIR
# remove false postive warning about chained assignment the default is 'warn'
pd.options.mode.chained_assignment = None
# setup for error logging
logger = logging.getLogger('calculate_prioity')
hdlr = logging.FileHandler(BASE_DIR + '/logs/calculate_prioity.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-I', '--Input_file', help='Path to Sact Input file this can be an absolute '
            'path or relative to the Django base directory. If this is not specfied the '
            'default path is "priority/IO/TEST_dump.csv".')
        parser.add_argument(
            '-O', '--Output_file', help='Path to Output file this can be an absolute '
            'path or relative to the Django base directory . If this is not specfied '
            'the default path is "priority/IO/QOS_output.csv".')
    def handle(self, *args, **options):
        # Arguments for Input file
        if options['Input_file'] == None:
            In_path = os.path.join(BASE_DIR, 'priority/IO/TEST_dump.csv')
        else:
            if os.path.isabs(options['Input_file']):
                In_path = options['Input_file']
            else:
                In_path = os.path.join(BASE_DIR, options['Input_file'])
        # Arguments for Output file
        if options['Output_file'] == None:
            Out_path = os.path.join(BASE_DIR, 'priority/IO/QOS_output.csv')
        else:
            if os.path.isabs(options['Output_file']):
                Out_path = options['Output_file']
            else:
                Out_path = os.path.join(BASE_DIR, options['Output_file'])
        # number of QOS levels
        QOS_levels = 4.0
        Today = date.today()
        # engine for reading/writing sql files
        # sqlite://<nohostname>/<pathtofile>
        dbpath=settings.DATABASES['default']['NAME']
        dbpath2=settings.DATABASES['default']['ENGINE']
        engine = create_engine('sqlite:///'+dbpath, echo=False)
        df = pd.read_csv(In_path, sep='|')
        # remove NANs
        df = df.dropna(how='any')
        # remove root from accounts list
        indexroot = df[df['Account'] == 'root'].index
        df.drop(indexroot, inplace=True)
        # convert cpu time from core seconds to core hours
        df.loc['CPUTimeRAW'] = df['CPUTimeRAW'].div(3600)
        # seperate into gpu and not gpu
        gpu = df[(df.Partition == "gpu") | (df.Partition == "xgpu")]
        compute = df[(df.Partition != "gpu") & (df.Partition != "xgpu")]
        # calculate the total raw cpu time used for each project
        cpu_sum = compute.groupby('Account')['CPUTimeRAW'].sum().astype(
            int).to_frame(name='cpu_sum')
        gpu_sum = gpu.groupby('Account')['CPUTimeRAW'].sum().astype(
            int).to_frame(name='gpu_sum')
        SCW = collect_AP()
        # combine the three data frames into one
        SCW = pd.merge(SCW, cpu_sum, on='Account', how='outer').fillna(0)
        SCW = pd.merge(SCW, gpu_sum, on='Account', how='outer').fillna(0)

        # Added to avoid problems in the event that projects are in the sacct 
        # Dump but not on Cogs (e.g. Cardiff users temporarily using Sunbird).
        # These would otherwise default to an Ap of Zero which crashes the np.log10 function.  
        SCW.Ap.loc[SCW.Ap == 0] = 50000
        #Calculate cpu/gpu hours used since last sacct dump.
        SCW['Cpu_New'] = SCW['cpu_sum'].subtract(SCW['CPU_hours'])
        SCW['Gpu_New'] = SCW['gpu_sum'].subtract(SCW['GPU_hours'])

        # calculate parameter such that K*log(Ap) has a max defined by
        # QOS_levels
        Max_Ap = SCW['Ap'].max()
        k = QOS_levels / np.log10(Max_Ap)
        # check if previous run was prioritezed and if so add the time since
        # last sactdump to total priortized time
        P = SCW['Qos'] > 0
        Prioritised = SCW[P]
        Prioritised['P_CPU'].add(Prioritised['Cpu_New'])
        Prioritised['P_GPU'].add(Prioritised['Gpu_New'])

        SCW.update(Prioritised)
        SCW['CPU_hours'] = SCW['CPU_hours'] + SCW['Cpu_New']
        SCW['GPU_hours'] = SCW['GPU_hours'] + SCW['Gpu_New']
        # calculate Priority
        Priority = (SCW['Ap'] - (SCW['P_CPU'] + SCW['P_GPU'] * 40)
                    ).to_frame(name='Priority_Sum').astype(int)
        Priority['QOS'] = SCW['Ap'].map(
            lambda a: k * np.log10(a)).round(0).astype(int)
        Priority['QOS'] = Priority['QOS'].where(
            Priority['Priority_Sum'] >= 0, 0)
        Priority['Account'] = SCW['Account']

        # create dataframe for output to django
        COGS_DB = pd.DataFrame(Priority['Account'], columns=['Account'])
        COGS_DB['QOS'] = Priority['QOS']
        COGS_DB['CPU_hours'] = SCW['CPU_hours']
        COGS_DB['GPU_hours'] = SCW['GPU_hours']
        COGS_DB['P_CPU'] = SCW['P_CPU']
        COGS_DB['P_GPU'] = SCW['P_GPU']
        COGS_DB['Ap'] = SCW['Ap']
        COGS_DB['Date'] = pd.date_range(
            start=Today, end=Today, periods=len(SCW.index))
        # output Acoount and QOS to pipe seperated csv file
        Priority.to_csv(
            Out_path,
            sep='|',
            columns=[
                'Account',
                'QOS'],
            index=False)
  # Warning output to clarify what happens when writing data twice on the same
  # day.
        if(slurm_priority.objects.filter(Date__year=Today.year, Date__month=Today.month, Date__day=Today.day).exists()):
            logger.warning(
            'Data for today already exists in django database, as such there will be multiple entries for each project in '
            'the priority table. However the project table will only contain data from this run.')
        # Write data to django database
        COGS_DB.to_sql(
            'priority_slurm_priority',
            index=False,
            con=engine,
            if_exists='append')
        # Write current Ap and Qos to Project database
        codes = Priority['Account'].tolist()
        Ap = COGS_DB['Ap'].astype(int).tolist()
        Qos = COGS_DB['QOS'].astype(int).tolist()
        Projects = Project.objects.filter(code__in=codes)
        for x, y, z in zip(codes, Ap, Qos):
            Projects.filter(code=x).update(Ap=y, Qos=z)


def collect_AP():
    priorities = Project.calculate_AP()
    Attpoints = pd.DataFrame(list(priorities.items()),columns=['Account','Ap'])
    yesterday = date.today() - timedelta(1)
    Priority_DB = slurm_priority.objects.filter(Date=yesterday)
    # If Priority DB exists merge in the Ap values
    if (Priority_DB.exists()):
        Priority_DATA = pd.DataFrame(
            list(
                Priority_DB.values(
                    'Account',
                    'CPU_hours',
                    'GPU_hours',
                    'P_CPU',
                    'P_GPU',
                    'Qos')))
        SCW = pd.merge(
            Priority_DATA,
            Attpoints,
            on='Account',
            how='left').fillna(0)
        return SCW
    else:
        # Priority DB is empty therfore create default values for projects that
        # are prioritized thease will then be added into the database during
        # the final append step.
        zeros = np.zeros(len(Attpoints['Account']))
        Attpoints['CPU_hours'] = zeros
        Attpoints['GPU_hours'] = zeros
        Attpoints['P_CPU'] = zeros
        Attpoints['P_GPU'] = zeros
        Attpoints['Qos'] = zeros
        return Attpoints
