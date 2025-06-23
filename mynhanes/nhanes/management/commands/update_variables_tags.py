from django.core.management.base import BaseCommand
from nhanes.services.update_variables_tags import update_variables_tags_from_csv


class Command(BaseCommand):
    help = 'Update variables tags from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='csv file with variables code and tags as columns'  # noqa E501
        )

    def handle(self, *args, **options):
        file = options['file']
        self.stdout.write(self.style.SUCCESS('Starting process...'))
        update_variables_tags_from_csv(file)
        self.stdout.write(self.style.SUCCESS('Completed process!'))
