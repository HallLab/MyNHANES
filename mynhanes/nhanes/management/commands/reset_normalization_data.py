# nhanes/management/commands/reset_normalizationdata.py

from django.core.management.base import BaseCommand
from django.db import connection
from nhanes.models import Data


class Command(BaseCommand):
    help = 'Delete all data from NormalizedData and reset the auto-increment ID'

    def handle(self, *args, **kwargs):
        # Deletar todos os dados do modelo NormalizedData
        Data.objects.filter(version=2).delete()
        self.stdout.write(self.style.SUCCESS('All data deleted from NormalizedData.'))

        # Reiniciar o índice auto-increment para a tabela NormalizedData
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='nhanes_normalizeddata';")  # noqa E501
            self.stdout.write(self.style.SUCCESS('Auto-increment ID reset to 0 for NormalizedData.'))  # noqa E501
