import os
import shutil

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import historical weekly storage stats from csv files.'

    def add_arguments(self, parser):
        parser.add_argument('--input_dir', required=True, help='Path to csv files to import', type=str)
        parser.add_argument('--output_dir', required=True, help='Path to move csv files to once processed', type=str)

    def handle(self, *args, **options):
        try:
            input_dir = options['input_dir']
            output_dir = options['output_dir']

            # Validate paths
            if os.path.exists(input_dir) is False:
                raise Exception(f'{input_dir} does not exist.')
            if os.path.exists(output_dir) is False:
                raise Exception(f'{output_dir} does not exist.')

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

                    # Once complete, move home and scratch files from
                    # input_dir to output_dir.
                    shutil.move(
                        home_file,
                        os.path.join(output_dir, filename),
                    )
                    shutil.move(
                        scratch_file,
                        os.path.join(output_dir, filename),
                    )

                    self.stdout.write(self.style.SUCCESS(f'Finished processing {os.path.join(input_dir, filename)}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(e))

        self.stdout.write(self.style.SUCCESS('Finished processing csv files.'))
