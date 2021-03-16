import os

from django.core.management.base import BaseCommand

# Usage: python3 manage.py import_historical_daily_compute --input_dir {input_dir}

class Command(BaseCommand):
    help = 'Import historical daily compute stats from bz2 files.'

    def add_arguments(self, parser):
        parser.add_argument('--input_dir', required=True, help='Path to bz2 files to import', type=str)

    def handle(self, *args, **options):
        try:
            input_dir = options['input_dir']

            # Validate path
            if os.path.exists(input_dir) is False:
                raise Exception(f'{input_dir} does not exist.')

            # Process bz2 files
            for filename in os.listdir(input_dir):
                if filename.endswith('bz2'):
                    self.stdout.write(self.style.SUCCESS(f'Processing {os.path.join(input_dir, filename)}'))

                    # Parse data attributes
                    filepath = os.path.join(input_dir, filename)

                    data = filename.split('_')
                    code = data[0]
                    system = None
                    month = data[1]
                    year = data[2][:4]

                    if code == 'hawk':
                        system = 'CF'
                    elif code == 'sunbird':
                        system = 'SW'
                    else:
                        self.stderr.write(self.style.ERROR(f'Invalid system code for {filepath}'))
                        continue

                    try:
                        # Extract file
                        os.system(f'bzip2 -d {filepath}')

                        # Process extracted file
                        filepath = filepath[:-4] # Remove .bz2 extension
                        for day in range(1, 32):
                            self.stdout.write(self.style.SUCCESS(f'Processing day {day} of {filepath}'))

                            # Call daily compute import script
                            os.system(
                                f"python3 manage.py import_daily_compute  \
                                    --file={filepath} \
                                    -d {day} \
                                    -m {month} \
                                    -y {year} \
                                    -s {system}"
                            )
                        self.stdout.write(self.style.SUCCESS(f'Finished processing {filepath}'))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(e))

        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing bz2 files.'))
