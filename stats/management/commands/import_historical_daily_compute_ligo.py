import os

from django.core.management.base import BaseCommand

# Usage: python3 manage.py import_historical_daily_compute_ligo --input_dir {input_dir}


class Command(BaseCommand):
    help = 'Import historical daily compute stats for LIGO from bz2 files.'

    def add_arguments(self, parser):
        parser.add_argument('--input_dir', required=True, help='Path to bz2 files to import', type=str)
    
    def parse_file(self, filepath, day, month, year, system):
        try:
            # Extract file
            os.system(f'bzip2 -d {filepath}')

            # Process extracted file
            filepath = filepath[:-4]  # Remove .bz2 extension

            self.stdout.write(self.style.SUCCESS(f'Processing day {day} of {filepath}'))

            # Call daily compute ligo import script
            os.system(
                f"python3 manage.py import_daily_compute_ligo  \
                    --file={filepath} \
                    -d {day} \
                    -m {month} \
                    -y {year} \
                    -s {system}"
            )
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
                self.stdout.write(self.style.SUCCESS(f'Processing {os.path.join(input_dir, filename)}'))

                system = 'CF'
                filepath = os.path.join(input_dir, filename)

                # Edge case
                if filename == 'all_20190702_20191204.tsv.bz2':
                    year = 2019
                    for month in range(7, 12+1):
                        for day in range(1, 31 + 1):
                            self.parse_file(filepath, day, month, year, system)
                
                # Normal cases
                elif filename.endswith('bz2') and 'merge' in filename:
                    data = filename.split('_')
                    try:
                        data.remove('ligo')
                        data.remove('merge')
                    except:
                        pass
                    month = data[0]
                    year = data[1]
                    for day in range(1, 31 + 1):
                        self.parse_file(filepath, day, month, year, system)

        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing bz2 files.'))

    
