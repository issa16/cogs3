import csv

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from users.models import CustomUser
from users.models import Profile


class Command(BaseCommand):
    help = 'Create or update user profile data from csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename')

    def handle(self, *args, **options):
        # Users will be added to the student user group by default
        group = Group.objects.get(name='student')
        filename = options['csv_filename']
        try:
            # Open input csv file
            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Get or create user
                    user, created = CustomUser.objects.get_or_create(
                        username=row['institutional_address'],
                        email=row['institutional_address'],
                        first_name=row['firstname'],
                        last_name=row['surname'],
                    )
                    if created:
                        user.set_password(CustomUser.objects.make_random_password())
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS('Successfully created user account: ' + row['institutional_address']))
                    else:
                        self.stdout.write(self.style.SUCCESS(row['institutional_address'] + ' already exists!'))

                    # Assign the user to a group
                    user.groups.add(group)

                    # Update user profile
                    profile = user.profile
                    profile.shibboleth_username = row['institutional_address']
                    profile.scw_username = row['new_scw_username']
                    profile.hpcw_username = row['hpcw_username']
                    profile.hpcw_email = row['hpcw_email']
                    # profile.institution - handled by user profile creation signal (users/signals.py)
                    profile.raven_username = row['raven_username']
                    profile.raven_email = row['raven_email']
                    profile.description = row['description']
                    profile.phone = row['phone']
                    profile.account_status = Profile.APPROVED
                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS('Successfully updated user profile: ' + row['institutional_address']))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Unable to open ' + filename))
