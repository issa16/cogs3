import os
from datetime import datetime

from django.core.management.base import BaseCommand

from . import find_date_range_of_ligo_file


class Command(BaseCommand):
    help = 'Import historical daily compute stats for LIGO from bz2 files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input_dir',
            required=True,
            help='Path to bz2 files to import',
            type=str,
        )

    def parse_file(self, filepath):
        try:
            # Call daily compute ligo import script
            os.system(f"python3 manage.py import_daily_compute_ligo --file {filepath}")
            self.stdout.write(self.style.SUCCESS(f'Finished processing {filepath}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

    def handle(self, *args, **options):
        try:
            input_dir = options['input_dir']

            # Validate path
            if os.path.exists(input_dir) is False:
                raise Exception(f'{input_dir} does not exist.')

            # Process bz2 files
            for filename in os.listdir(input_dir):
                if filename.endswith('.bz2'):
                    try:
                        filepath = os.path.join(input_dir, filename)
                        self.stdout.write(self.style.SUCCESS(f'Processing {filepath}'))

                        # Extract file
                        os.system(f'bzip2 -d {filepath}')

                        # Process extracted file
                        filepath = filepath[:-4]  # Remove .bz2 extension
                        self.parse_file(filepath)

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(e))

        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing bz2 files.'))
