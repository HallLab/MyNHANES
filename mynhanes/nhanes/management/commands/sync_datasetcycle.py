from django.core.management.base import BaseCommand
from nhanes.workprocess.sync_workprocess import check_and_sync_datasetcycle


class Command(BaseCommand):
    help = 'Check and Sync WorkProcess'

    def handle(self, *args, **options):
        import_success = check_and_sync_datasetcycle()

        if import_success:
            self.stdout.write(self.style.SUCCESS(
                'DatasetCycle model sync successfully')
            )
        else:
            self.stdout.write(self.style.ERROR('DatasetCycle model sync failed'))
