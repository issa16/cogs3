import os

from django.core.management.base import BaseCommand

# Usage: python3 manage.py import_historical_weekly_storage --input_dir {input_dir}

class Command(BaseCommand):
    help = 'Import historical weekly storage stats from csv files.'

    def add_arguments(self, parser):
        parser.add_argument('--input_dir', required=True, help='Path to csv files to import', type=str)

    def handle(self, *args, **options):
        try:
            input_dir = options['input_dir']

            # Validate paths
            if os.path.exists(input_dir) is False:
                raise Exception(f'{input_dir} does not exist.')

            # Process csv files
            for filename in os.listdir(input_dir):
                if filename.endswith('csv') and 'home' in filename:
                    self.stdout.write(self.style.SUCCESS(f'Processing {os.path.join(input_dir, filename)}'))

                    # Parse data attributes
                    home_file = os.path.join(input_dir, filename)
                    scratch_file = os.path.join(
                        input_dir,
                        filename.replace('home', 'scratch'),
                    )
                    data = filename.split('_')
                    date = data[4]
                    day = date[6:8]
                    month = date[4:6]
                    year = date[0:4]
                    code = 'CF'  # Double check

                    # Call weekly storage import script
                    os.system(
                        f"python3 manage.py import_weekly_storage \
                            --homefile={home_file} \
                            --scratchfile={scratch_file} \
                            -d {day} \
                            -m {month} \
                            -y {year} \
                            -s {code}"
                    )

                    self.stdout.write(self.style.SUCCESS(f'Finished processing {os.path.join(input_dir, filename)}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing csv files.'))
