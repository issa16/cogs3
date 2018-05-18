import csv

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from users.models import CustomUser
from users.models import Profile


class Command(BaseCommand):
    help = 'Create or update shibboleth user profile data.'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename')

    def handle(self, *args, **options):
        filename = options['csv_filename']
        try:
            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    user, created = CustomUser.objects.get_or_create(
                        username=row['institutional_address'],
                        email=row['institutional_address'],
                        first_name=row['firstname'],
                        last_name=row['surname'],
                        is_shibboleth_login_required=True,
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS('Successfully created user account: ' + row['institutional_address']))
                    else:
                        self.stdout.write(self.style.SUCCESS(row['institutional_address'] + ' already exists!'))

                    # Update shibboleth user profile.
                    profile = user.profile
                    profile.scw_username = row['new_scw_username']
                    profile.hpcw_username = row['hpcw_username']
                    profile.hpcw_email = row['hpcw_email']
                    profile.raven_username = row['raven_username']
                    profile.raven_email = row['raven_email']
                    profile.description = row['description']
                    profile.phone = row['phone']
                    profile.account_status = Profile.AWAITING_APPROVAL
                    profile.shibboleth_id = row['institutional_address']

                    # Pending new fields?
                    # profile.department = row['department']?
                    # profile.orcid = row['orcid']?
                    # profile.scopus = row['scopus']?
                    # profile.homepage = row['homepage']?
                    # profile.cronfa = row['cronfa']?

                    profile.save()
                    self.stdout.write(
                        self.style.SUCCESS('Successfully updated user profile: ' + row['institutional_address']))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Unable to open ' + filename))
