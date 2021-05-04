from django.core.management.base import BaseCommand
from project.models import Project


class Command(BaseCommand):
    help = 'Copy project PI text field to new PI format fields.'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            try:
                name, position, email = project.pi.split(',')
                project.pi_name = name.title().strip()
                project.pi_position = position.title().strip()
                project.pi_email = email.lower().strip()
                project.save()
                msg = f'{project.code} Updated.'
                self.stdout.write(self.style.SUCCESS(msg))
            except Exception as e:
                msg = f'{project.code} {e}'
                self.stdout.write(self.style.ERROR(msg))
