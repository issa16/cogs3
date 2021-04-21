import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import historical user last login dates.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input_dir',
            required=True,
            help='Path to csv files to import',
            type=str,
        )

    def handle(self, *args, **options):
        try:
            input_dir = options['input_dir']

            # Validate path
            if os.path.exists(input_dir) is False:
                raise Exception(f'{input_dir} does not exist.')

            # Process csv files
            for filename in os.listdir(input_dir):
                if filename.endswith(".csv"):
                    filepath = os.path.join(input_dir, filename)
                    self.stdout.write(self.style.SUCCESS(f'Processing {filepath}'))
                    os.system(f'python3 manage.py import_user_last_login --file {filepath}')
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing csv files.'))
