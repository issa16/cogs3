import csv

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import Weekly Stats Storage Projects CF from csv file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_filename')

    def handle(self, *args, **options):
        pass
