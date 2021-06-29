import datetime
import os

import pandas as pd
from django.core.management.base import BaseCommand
from project.models import Project, ProjectUserMembership
from stats.models import ComputeDaily
from stats.slurm.StatsParserCondorLigo import StatsParserCondorLigo
from system.models import AccessMethod, Application, Partition
from users.models import CustomUser, Profile

'''
15/12/2020
The userName supplied in the LIGO file does not match the
format expected in cogs3. This issue has been raised with
ARCCA and agreed to be resolved at a later date.

11/01/2021
It has been agreed to create a new user account in cogs3
if the user within the LIGO daily compute file is not found.
The user will be created as an external account.
'''


class Command(BaseCommand):
    help = 'Process a LIGO log file stats for a particular date.'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', dest="acctf", required=True, help='Condor ligo log file to parse', type=str)
        parser.add_argument('-d', required=True, help="day", type=int, dest='sday')
        parser.add_argument('-m', required=True, help="month", type=int, dest='smonth')
        parser.add_argument('-y', required=True, help="year", type=int, dest='syear')
        parser.add_argument('-s', required=True, help="system/cluster code", dest='ssys')

    def handle(self, *args, **options):
        try:
            acctf = options['acctf'].strip()
            sday = options['sday'].strip()
            smonth = options['smonth'].strip()
            syear = options['syear'].strip()
            ssys = options['ssys'].strip()

            if not os.path.isfile(acctf):
                raise Exception(f'{acctf} not found')

            my_date=datetime.datetime(syear, smonth, sday)

            msg = f'DailyStatsParserLigo started for {my_date} file {acctf}'
            self.stdout.write(self.style.SUCCESS(msg))

            my_date_only=datetime.date(year=my_date.year,month=my_date.month,day=my_date.day)
            yesterday=datetime.date.today()-datetime.timedelta(days=1)

            sp = StatsParserCondorLigo(acctf, my_date)
            sp.ParseNow()

            msg = f'INFO: Parsed array size {sp.getArraySize()} jobs'
            self.stdout.write(self.style.SUCCESS(msg))

            count = 0
            countNew = 0
            countUpdated = 0
            sumWall = datetime.timedelta(0)

            for i in sp.getResultsArray():
                # Find the project
                try:
                    myProject = Project.objects.get(code__iexact=i['projectCode'])
                except Project.DoesNotExist:
                    msg = f"No matching project: {i['projectCode']}"
                    self.stdout.write(msg)
                    continue
                # Find or create user
                try:
                    firstname, lastname = i['userName'].split('.')
                    email = f'{firstname}.{lastname}@ligo.org'.lower()
                    user, created = CustomUser.objects.get_or_create(
                        username=f'{firstname}.{lastname}'.lower(),
                        email=email,
                        first_name=firstname.title(),
                        last_name=lastname.title(),
                        is_shibboleth_login_required=False,
                    )
                    if created:
                        # Reset password
                        user.set_password(CustomUser.objects.make_random_password())
                        user.save()

                        # Create user profile
                        profile = user.profile
                        profile.description = 'Imported via LIGO daily compute script'
                        profile.account_status = Profile.APPROVED
                        profile.save()

                        # Create a user membership
                        project_user_membership = ProjectUserMembership(
                            user=user,
                            project=myProject,
                            status=ProjectUserMembership.AUTHORISED,
                            date_joined=date.today(),
                        )
                        project_user_membership.save()

                        msg = f'Successfully created user account, profile and project membership for {email}'
                        self.stdout.write(self.style.SUCCESS(msg))
                    else:
                        msg = f'{email} already exists.'
                        self.stdout.write(self.style.SUCCESS(msg))
                    myUser = user
                except Exception as e:
                    self.stdout.write(self.style.ERROR(e))
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
                        self.stdout.write(f'Created new Application {myExecApp}')
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

                sumWall += i['wallTime']

                # Check for existing record for the matching dimensions of measurement
                obj, created = ComputeDaily.objects.get_or_create(
                    user=myUser,
                    project=myProject,
                    partition=myPartition,
                    application=myExecApp,
                    access_method=mySubMethod,
                    number_processors=myExecNCPU,
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

            msg = f'SUM WALL TIME={sumWall}'
            self.stdout.write(self.style.SUCCESS(msg))

            msg = f'MAX WALL TIME={datetime.timedelta(hours=(24 * ((40 * 60) + (24 * 60))))}'
            self.stdout.write(self.style.SUCCESS(msg))

            
        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
