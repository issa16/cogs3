import datetime
import os

from django.core.management.base import BaseCommand
from project.models import Project
from stats.models import ComputeDaily
from stats.slurm.StatsParserSlurm import StatsParserSlurm
from system.models import AccessMethod, Application, Partition
from users.models import Profile

from .util import get_system


class Command(BaseCommand):
    help = 'Import compute daily stats from slurm completion log file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            required=True,
            help='Slurm completion log file to parse',
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

            sp = StatsParserSlurm(stats_file, date)
            sp.ParseNow()

            msg = f'INFO: Parsed array size {sp.getArraySize()} jobs'
            self.stdout.write(self.style.SUCCESS(msg))

            count = 0
            countNew = 0
            countUpdated = 0

            for i in sp.getResultsArray():
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
                    myExecApp = Application.objects.get(name__iexact=i['execApp'])
                except Application.DoesNotExist:
                    msg = f"No matching application profile: {i['execApp']}"
                    self.stdout.write(msg)
                    continue
                # Find the partition (queue)
                try:
                    modParitionName = system + "-" + i['execQueue']
                    myParition = Partition.objects.get(name__iexact=modParitionName)
                except Partition.DoesNotExist:
                    msg = f"No matching partition entry: {i['modParitionName']}"
                    self.stdout.write(msg)
                    continue
                # Check for existing record for the matching dimensions of measurement
                obj, created = ComputeDaily.objects.get_or_create(
                    user=myUser,
                    project=myProject,
                    partition=myParition,
                    application=myExecApp,
                    access_method=mySubMethod,
                    number_processors=i['execNCPU'],
                    date=date,
                    defaults={
                        'number_jobs': i['nJobs'],
                        'wait_time': i['waitTime'],
                        'cpu_time': i['cpuTime'],
                        'wall_time': i['wallTime'],
                    }
                )
                if not created:
                    obj.number_jobs = i['nJobs']
                    obj.wait_time = i['waitTime']
                    obj.cpu_time = i['cpuTime']
                    obj.wall_time = i['wallTime']
                    obj.save()
                    countUpdated += 1
                    msg = (
                        f"INFO: Updated: {obj.id} {date} {obj.user} {obj.project} {obj.partition} {obj.application} {obj.access_method}"
                        f" {obj.number_processors} {i['waitTime']} {i['cpuTime']} {i['wallTime']} {i['nJobs']}"
                    )
                else:
                    countNew += 1
                    msg = (
                        f"INFO: Added new: {obj.id} {date} {obj.user} {obj.project} {obj.partition} {obj.application} {obj.access_method}"
                        f" {obj.number_processors} {i['waitTime']} {i['cpuTime']} {i['wallTime']} {i['nJobs']}"
                    )

                self.stdout.write(self.style.SUCCESS(msg))
                count += 1

            msg = f'END - {countNew} new records, {countUpdated} updated records'
            self.stdout.write(self.style.SUCCESS(msg))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
