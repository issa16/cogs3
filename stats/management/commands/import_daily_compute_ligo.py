import datetime
import os

from django.core.management.base import BaseCommand
from project.models import Project
from stats.models import ComputeDaily
from stats.slurm.StatsParserCondorLigo import StatsParserCondorLigo
from system.models import AccessMethod, Application, Partition
from users.models import Profile

from .util import get_system


class Command(BaseCommand):
    help = 'Process a LIGO log file stats for a particular date.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            required=True,
            help='Condor ligo log file to parse',
            type=str,
        )
        parser.add_argument('-d', required=True, help='Day', type=int)
        parser.add_argument('-m', required=True, help='Month', type=int)
        parser.add_argument('-y', required=True, help='Year', type=int)
        parser.add_argument('-s', required=True, help='System', type=str)

    def handle(self, *args, **options):
        try:
            stats_file = options['file'].strip()
            day = options['d']
            month = options['m']
            year = options['y']
            system = options['s'].strip()

            if not os.path.isfile(stats_file):
                raise Exception(f'{stats_file} not found')

            # Verify system
            get_system(system)

            date = datetime.datetime(day=day, month=month, year=year)

            msg = f'DailyStatsParserLigo started for {date} file {stats_file}'
            self.stdout.write(self.style.SUCCESS(msg))

            sp = StatsParserCondorLigo(stats_file, date)
            sp.ParseNow()

            msg = f'INFO: Parsed array size {sp.getArraySize()} jobs'
            self.stdout.write(self.style.SUCCESS(msg))

            count = 0
            countNew = 0
            countUpdated = 0
            sumWall = datetime.timedelta(0)

            for i in sp.getResultsArray():
                '''
                15/12/2020
                The userName supplied in the LIGO file does not match the
                format expected in cogs3. This issue has been raised with
                arcca and agreed to resolved at a later date.

                Notes
                -----
                Some Cardiff users appear to have multiple citizenship on both
                Hawk and LIGO. Therefore care is needed when applying a
                solution as the users may already exist in cogs3.

                Possible solutions:
                - Add a new ligo_username field to the users profile. Would
                  result in Cardiff users having two accounts.
                '''
                # Find the user record
                try:
                    userProfile = Profile.objects.get(scw_username__iexact=i['userName'])
                    myUser = userProfile.user
                except Profile.DoesNotExist:
                    msg = f"No matching user: {i['userName']}"
                    self.stdout.write(msg)
                    continue
                # Find the project record
                try:
                    myProject = Project.objects.get(code__iexact=i['projectCode'])
                except Project.DoesNotExist:
                    msg = f"No matching project: {i['projectCode']}"
                    self.stdout.write(msg)
                    continue
                # Find the submission method
                try:
                    mySubMethod = AccessMethod.objects.get(name__iexact=i['subMethod'])
                except AccessMethod.DoesNotExist:
                    msg = f"No matching Access/Submission Method: {i['subMethod']}"
                    self.stdout.write(msg)
                    continue
                # Find the execution application profile
                try:
                    myExecApp, state = Application.objects.get_or_create(
                        name__iexact=i['execApp'],
                        defaults={'name': i['execApp']},
                    )
                    if state:
                        print("Created new Application", myExecApp)
                except Application.DoesNotExist:
                    msg = f"No matching application profile: {i['execApp']}"
                    self.stdout.write(msg)
                    continue
                if not myExecApp:
                    msg = "ERROR: app not parsed from ligo search tag record"
                    self.stdout.write(msg)
                '''
                NumberOfProcessors model has been removed and replaced with a
                field in the ComputeDaily model.
                '''
                myExecNCPU = i['execNCPU']
                # Find the partition (queue)
                try:
                    myPartition = Partition.objects.get(name__iexact=i['execQueue'])
                except Partition.DoesNotExist:
                    msg = f"No matching partition entry: {i['execQueue']}"
                    self.stdout.write(msg)
                    continue
                if not myPartition:
                    msg = "ERROR: queue not parsed from ligo machineattr record"
                    self.stdout.write(msg)

                #debug
                #print("myUser="+str(myUser)+" myProject="+str(myProject)+" myPartition="+str(myPartition)+" myExecApp="+str(myExecApp)+" mySubMethod="+str(mySubMethod)+" myExecNCPU="+str(myExecNCPU)+" nJobs="+str(i['nJobs'])+" waitTime="+str(i['waitTime'])+" cpuTime="+str(i['cpuTime'])+" wallTime="+str(i['wallTime']))
                sumWall += i['wallTime']

                ## Check for existing record for the matching dimensions of measurement
                obj, created = ComputeDaily.objects.get_or_create(
                    user=myUser,
                    project=myProject,
                    partition=myPartition,
                    application=myExecApp,
                    access_method=mySubMethod,
                    number_processors=myExecNCPU,  #
                    date=date,
                    defaults={
                        'number_jobs': i['nJobs'],
                        'wait_time': i['waitTime'],
                        'cpu_time': i['cpuTime'],
                        'wall_time': i['wallTime'],
                    }
                )
                if not created:  # i.e. update!
                    obj.number_jobs = i['nJobs']
                    obj.wait_time = i['waitTime']
                    obj.cpu_time = i['cpuTime']
                    obj.wall_time = i['wallTime']
                    obj.save()
                    countUpdated += 1
                    #print("INFO: Updated:",obj.id,date,obj.user,obj.project,obj.partition,obj.application,obj.access_method,obj.number_processors,i['waitTime'],i['cpuTime'],i['wallTime'],i['nJobs'])
                else:
                    countNew += 1
                    #print("INFO: Added new:",obj.id,date,obj.user,obj.project,obj.partition,obj.application,obj.access_method,obj.number_processors,i['waitTime'],i['cpuTime'],i['wallTime'],i['nJobs'])

            count += 1

            msg = f'END - {countNew} new records, {countUpdated} updated records'
            self.stdout.write(self.style.SUCCESS(msg))

            msg = f'SUM WALL TIME={sumWall}'
            self.stdout.write(self.style.SUCCESS(msg))

            msg = f'MAX WALL TIME={datetime.timedelta(hours=(24 * ((40 * 60) + (24 * 60))))}'
            self.stdout.write(self.style.SUCCESS(msg))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
