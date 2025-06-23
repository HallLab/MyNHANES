from django.core.management.base import BaseCommand
from nhanes.models import Data  # Substitua 'myapp' pelo nome do seu app


class Command(BaseCommand):
    help = 'Clear all entries in the Logs table'

    def handle(self, *args, **kwargs):
        try:
            deleted_count, _ = Data.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(
                f'Successfully deleted {deleted_count} entries from the Logs table.'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing Logs table: {e}'))
