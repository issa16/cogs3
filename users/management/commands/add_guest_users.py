import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from users.models import CustomUser
from users.models import Profile


class Command(BaseCommand):
    help = 'Create Guest user accounts.'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename')

    def handle(self, *args, **options):
        try:
            filename = options['csv_filename']
            with open(filename, newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            user, created = CustomUser.objects.get_or_create(
                                username=row['institutional_address'].lower(),
                                email=row['institutional_address'].lower(),
                                first_name=row['firstname'].title(),
                                last_name=row['surname'].title(),
                                is_shibboleth_login_required=False,
                            )
                            if created:
                                user.set_password(CustomUser.objects.make_random_password())
                                user.save()
                                message = 'Successfully created user account: {email}'.format(
                                    email=row['institutional_address'])
                                self.stdout.write(self.style.SUCCESS(message))
                            else:
                                message = '{email} already exists.'.format(email=row['institutional_address'])
                                self.stdout.write(self.style.SUCCESS(message))

                            profile = user.profile
                            profile.hpcw_username = row['hpcw_username'].lower()
                            profile.hpcw_email = row['hpcw_email'].lower()
                            profile.raven_username = row['raven_username']
                            if row['raven_uid']:
                                profile.uid_number = int(row['raven_uid'])
                            profile.raven_email = row['raven_email'].lower()
                            profile.description = row['description']
                            profile.phone = row['phone']
                            profile.account_status = Profile.AWAITING_APPROVAL
                            profile.save()

                            message = 'Successfully updated user profile: {email}'.format(
                                email=row['institutional_address'])
                            self.stdout.write(self.style.SUCCESS(message))
                    except Exception as e:
                        message = '{error}\n{row}'.format(error=e, row=row)
                        self.stdout.write(self.style.ERROR(message))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Unable to open ' + filename))
