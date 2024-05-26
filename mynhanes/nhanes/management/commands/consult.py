from django.core.management.base import BaseCommand
from nhanes.services.consult import extract_data
import json


class Command(BaseCommand):
    help = 'Consult NHANES DB and extract data.'

    def add_arguments(self, parser):
        # Argumento opcional para filtros
        parser.add_argument(
            '--filters',
            type=json.loads,  # Assume que serão passados como string JSON
            help='Filters in JSON format. Example: \'{"field": "cycle__cycle_name", "operator": "exact", "value": "2017-2018"}\''  # noqa E501
        )
        # Argumento opcional para o nome do arquivo
        parser.add_argument(
            '--filename',
            type=str,
            help='Filename to save the extracted data as CSV.'
        )

    def handle(self, *args, **options):
        filters = options['filters'] if 'filters' in options else None
        filename = options['filename'] if 'filename' in options else None

        self.stdout.write(self.style.SUCCESS('Starting Consult...'))
        data = extract_data(filters=filters, filename=filename)
        if data:
            self.stdout.write(self.style.SUCCESS(
                'Data successfully extracted and saved to CSV.'
                )
                )
        else:
            self.stdout.write(self.style.ERROR('Failed to extract data.'))
        self.stdout.write(self.style.SUCCESS('Consult completed!'))


"""
python manage.py consult --filters '{"field": "cycle__cycle_name", "operator": "exact", "value": "2017-2018"}' --filename 'output.csv'  # noqa E501

"""