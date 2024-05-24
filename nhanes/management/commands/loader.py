from django.core.management.base import BaseCommand
from nhanes.services.loader import download_nhanes_files


class Command(BaseCommand):
    help = 'Download NHANES files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting download...'))
        download_nhanes_files()
        self.stdout.write(self.style.SUCCESS('Download completed!'))
