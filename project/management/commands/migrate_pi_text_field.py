from django.core.management.base import BaseCommand
from project.models import Project


class Command(BaseCommand):
    help = 'Copy project PI text field to new PI format fields.'    def handle(self, *args, **options):

    def handle(self, *args, **options):
        for project in Project.objects.all():
            if ' and ' in project.pi:
                # Handle multiple PIs format: Name, Position, Email and Name, Position, Email
                try:
                    pi_1, p1_2 = project.pi.split(' and ')
                    name_1, position_1, email_1 = pi_1.split(',')
                    name_2, position_2, email_2 = p1_2.split(',')
                    project.pi_name = f'{name_1.title().strip()}; {name_2.title().strip()}'
                    project.pi_position = f'{position_1.strip()}; {position_2.strip()}'
                    project.pi_email = f'{email_1.lower().strip()}; {email_2.lower().strip()}'
                    project.save()
                    msg = f'{project.code} Updated.'
                    self.stdout.write(self.style.SUCCESS(msg))
                except Exception as e:
                    msg = f'{project.code} {e}'
                    self.stdout.write(self.style.ERROR(msg))
            elif ',' in project:
                # Handle single PI format: Name, Position, Email
                try:
                    name, position, email = project.pi.split(',')
                    project.pi_name = name.title().strip()
                    project.pi_position = position.strip()
                    project.pi_email = email.lower().strip()
                    project.save()
                    msg = f'{project.code} Updated.'
                    self.stdout.write(self.style.SUCCESS(msg))
                except Exception as e:
                    msg = f'{project.code} {e}'
                    self.stdout.write(self.style.ERROR(msg))
            else:
                try: # Handle single values
                    project.pi_name = project.pi
                    project.pi_position = ''
                    project.pi_email = ''
                    project.save()
                    msg = f'{project.code} Updated.'
                    self.stdout.write(self.style.SUCCESS(msg))
                except Exception as e:
                    msg = f'{project.code} {e}'
                    self.stdout.write(self.style.ERROR(msg))
