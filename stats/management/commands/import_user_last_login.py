import csv
import datetime
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from users.models import Profile, UserLastLogin


class Command(BaseCommand):
    help = 'Update user last login dates.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            required=True,
            help='csv format file to parse',
            type=str,
        )

    def handle(self, *args, **options):
        try:
            login_file = options['file'].strip()

            if not os.path.isfile(login_file):
                raise Exception(f'{login_file} not found')

            msg = (
                f'Last Login Sync, running on {os.uname()[1]} at {datetime.datetime.now()}',
                f'\tReading file {login_file}'
            )
            self.stdout.write(self.style.SUCCESS(msg))

            # Read each line of file
            with open(login_file, newline='') as myFile:
                llreader = csv.reader(myFile)
                for row in llreader:
                    luser = row[0]
                    lunixtime = ""
                    if row[1] != "":
                        lunixtime = row[1]
                    else:
                        lunixtime = 0
                    lreadabledate = ""
                    if row[2] != "":
                        lreadabledate = datetime.datetime.strptime(row[2], '%d/%m/%Y')
                    else:
                        lreadabledate = datetime.datetime(1970, 1, 1)
                    lhost = ""
                    if row[3] != "":
                        lhost = row[3]
                    else:
                        lhost = ""

                    # See if LastLogin entry already exists
                    found = True
                    lluser = ""
                    llentry = ""
                    try:
                        llProfile = Profile.objects.get(scw_username__iexact=luser)
                        lluser = llProfile.user
                        llentry = UserLastLogin.objects.get(user=lluser)
                    except ObjectDoesNotExist:
                        found = False

                    if found:  # Update
                        msg = f'\t\tupdate {luser} {lunixtime} {lreadabledate} {lhost}'
                        self.stdout.write(self.style.SUCCESS(msg))
                        llentry.last_login_unix_time = lunixtime
                        llentry.last_login_time = lreadabledate
                        llentry.last_login_host = lhost
                        llentry.save()
                    else:  # Create new
                        try:
                            msg = f'\t\tcreate {luser} {lunixtime} {lreadabledate} {lhost}'
                            self.stdout.write(self.style.SUCCESS(msg))
                            llProfile = Profile.objects.get(scw_username__iexact=luser)
                            lluser = llProfile.user
                            lle = UserLastLogin(
                                user=lluser,
                                last_login_unix_time=lunixtime,
                                last_login_time=lreadabledate,
                                last_login_host=lhost,
                            )
                            lle.save()
                        except ObjectDoesNotExist:
                            msg = f'\t\t\tCould not find user {luser}'
                            self.stdout.write(self.style.ERROR(msg))
        except Exception as e:
            self.stdout.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('END'))
