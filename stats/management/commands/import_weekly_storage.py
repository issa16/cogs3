import csv
import datetime
import os

from django.core.management.base import BaseCommand
from project.models import Project
from stats.models import StorageWeekly

from .util import get_system


class Command(BaseCommand):
    help = 'Import weekly storage stats from csv files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--homefile',
            required=True,
            help='Home stats file to parse',
            type=str,
        )
        parser.add_argument(
            '--scratchfile',
            required=True,
            help='Scratch stats file to parse',
            type=str,
        )
        parser.add_argument('-d', required=True, help='Day', type=int)
        parser.add_argument('-m', required=True, help='Month', type=int)
        parser.add_argument('-y', required=True, help='Year', type=int)
        parser.add_argument('-s', required=True, help='System', type=str)

    def verify_day_is_saturday(self, date):
        if date.weekday() != 5:
            raise Exception(f'Date specified ({date}) is not a Saturday')

    def parse_stats(self, stats_file):
        data = []
        for row in stats_file:
            data.append({
                'project': row['project'],
                'space_used': row['space_used'],
                'files_used': row['files_used'],
            })
        return data

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        try:
            home_file = options['homefile'].strip()
            scratch_file = options['scratchfile'].strip()
            day = options['d']
            month = options['m']
            year = options['y']
            system = options['s'].strip()

            # Verify date
            date = datetime.datetime(day=day, month=month, year=year)
            self.verify_day_is_saturday(date)

            # Verify system
            system = get_system(system)

            # Read in home stats
            field_names = ['project', 'space_used', 'files_used']
            if not os.path.isfile(home_file):
                raise Exception(f'{home_file} not found')
            home_file_data = csv.DictReader(open(home_file), field_names)
            home_data = self.parse_stats(home_file_data)

            # Read in scratch stats
            if not os.path.isfile(scratch_file):
                raise Exception(f'{scratch_file} not found')
            scratch_file_data = csv.DictReader(open(scratch_file), field_names)
            scratch_data = self.parse_stats(scratch_file_data)

            # Create or update databases rows
            for home_stat in home_data:

                # Find the project code
                try:
                    project = Project.objects.get(code__iexact=home_stat['project'])
                except Project.DoesNotExist:
                    msg = f"No matching database project {home_stat['project']}...skipping"
                    self.stdout.write(self.style.ERROR(msg))
                    continue

                # Find scratch dict
                scratch_stat = next(
                    (item for item in scratch_data if item['project'] == home_stat['project']),
                    None,
                )
                if scratch_stat is None:
                    msg = f"Couldn't find scratch stats for {home_stat['project']}...skipping"
                    self.stdout.write(self.style.ERROR(msg))
                    continue

                obj, created = StorageWeekly.objects.update_or_create(
                    project=project,
                    date=date,
                    system=system,
                    defaults={
                        'home_space_used': home_stat['space_used'],
                        'home_files_used': home_stat['files_used'],
                        'scratch_space_used': scratch_stat['space_used'],
                        'scratch_files_used': scratch_stat['files_used']
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing csv files.'))
        self.stdout.write(self.style.SUCCESS(f'New records: {created_count}, Updated records: {updated_count}\n'))
