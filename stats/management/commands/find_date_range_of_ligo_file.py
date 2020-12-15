import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Process a LIGO log file to find dates included.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--file',
            required=True,
            help='LIGO log file to parse',
            type=str,
        )

    def handle(self, *args, **options):
        try:
            log_file = options['file'].strip()

            if not os.path.isfile(log_file):
                raise Exception(f'{log_file} not found')

            fields = [
                'JobID',
                'Owner',
                'LigoSearchTag',
                'Qdate',
                'JobStartDate',
                'CompletionDate',
                'MachineAttr',
                'RequestCpus',
                'CPUsUsage',
                'RemoteUserCPU',
                'RemoteSysCPU',
                'RequestMemory',
                'MemoryUsage',
            ]

            earliest = 4102444800  # 2100-01-01T00:00:00
            latest = 0
            count = 0

            with open(log_file) as tsvfile:
                reader = csv.DictReader(
                    tsvfile,
                    dialect="excel-tab",
                    fieldnames=fields,
                )
                for row in reader:
                    count += 1
                    mydate = 0
                    if row['CompletionDate'] is not None:
                        mydate = int(row['CompletionDate'])
                    if mydate != 0:
                        if mydate < earliest:
                            earliest = mydate
                        if mydate > latest:
                            latest = mydate

            self.stdout.write(self.style.SUCCESS(f'Total jobs: {count}'))
            self.stdout.write(self.style.SUCCESS(f'Earliest: {datetime.utcfromtimestamp(earliest)}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
