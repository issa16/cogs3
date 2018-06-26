import csv
import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from project.models import Project
from project.models import ProjectCategory
from project.models import ProjectFundingSource
from project.models import ProjectUserMembership
from users.models import Profile


class Command(BaseCommand):
    help = 'Import HPCW projects from a csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename')

    def handle(self, *args, **options):
        try:
            filename = options['csv_filename']
            with open(filename, newline='', encoding='ISO-8859-1') as csvfile:
                next(csvfile)
                reader = csv.reader(csvfile, delimiter=',')
                self.parse_projects(reader)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Unable to open ' + filename))

    def parse_projects(self, reader):
        for row in reader:
            try:
                with transaction.atomic():
                    self.parse_project(row)
                    self.parse_project_membership(row)
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))

    def parse_project(self, data):
        _, created = Project.objects.get_or_create(
            legacy_hpcw_id=data[0],
            title='Untitled' if data[2] is '' else data[2],
            description='',
            institution_reference='',
            pi=data[5].title(),
            tech_lead=Profile.objects.get(hpcw_username__iexact=data[6].lower()).user,
            category=ProjectCategory.objects.get(name='Standard Projects - Internally Funded'),
            funding_source=ProjectFundingSource.objects.get(name='N/A'),
            start_date=datetime.datetime.strptime(data[1], '%d/%m/%Y'),
            end_date=datetime.datetime.strptime(data[1], '%d/%m/%Y'),
            allocation_cputime=0,
            allocation_memory=0,
            allocation_storage_home=0,
            allocation_storage_scratch=0,
            status=Project.AWAITING_APPROVAL,
            notes='Imported HPCW Project.',
        )
        if created:
            message = 'Successfully created project {code}.'.format(code=data[0])
            self.stdout.write(self.style.SUCCESS(message))
        else:
            message = 'Project {code} already exists.'.format(code=data[0])
            self.stdout.write(self.style.SUCCESS(message))

    def parse_project_membership(self, data):
        project_member_col_index = 8
        while (data[project_member_col_index].strip()):
            user = Profile.objects.get(hpcw_username__iexact=data[project_member_col_index].lower()).user
            _, created = ProjectUserMembership.objects.get_or_create(
                project=Project.objects.get(legacy_hpcw_id=data[0]),
                user=user,
                status=ProjectUserMembership.AWAITING_AUTHORISATION,
                date_joined=datetime.datetime.now(),
            )
            if created:
                message = 'Successfully created project user membership for {hpcw_username}({user}).'.format(
                    hpcw_username=user.profile.hpcw_username,
                    user=user,
                )
                self.stdout.write(self.style.SUCCESS(message))
            else:
                message = 'Project user membership for {hpcw_username} ({user}) already exists.'.format(
                    hpcw_username=user.profile.hpcw_username,
                    user=user,
                )
                self.stdout.write(self.style.SUCCESS(message))
            project_member_col_index += 1
