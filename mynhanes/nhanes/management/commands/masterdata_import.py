from django.core.management.base import BaseCommand
from nhanes.workprocess.masterdata_import import masterdata_import


class Command(BaseCommand):
    help = 'Import Master Data from CSV files'

    def handle(self, *args, **options):
        import_success = masterdata_import()

        if import_success:
            self.stdout.write(self.style.SUCCESS(
                'Master Data import completed successfully')
            )
        else:
            self.stdout.write(self.style.ERROR('Master Data import failed'))
