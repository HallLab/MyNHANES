from django.core.management.base import BaseCommand
from mynhanes.nhanes.services.workprocess_ingestion import download_nhanes_files


class Command(BaseCommand):
    help = 'Download NHANES files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            help='csv to only save the files or db to load on db'  # noqa E501
        )

    def handle(self, *args, **options):
        type_load = options['type'] if 'type' in options else 'db'
        self.stdout.write(self.style.SUCCESS('Starting download...'))
        download_nhanes_files(type_load)
        self.stdout.write(self.style.SUCCESS('Download completed!'))
