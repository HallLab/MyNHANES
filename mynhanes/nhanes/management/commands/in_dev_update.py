from django.core.management.base import BaseCommand, CommandError
from nhanes.services.deploy import update_datasetcontrol_standby  # noqa E501


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument(
            '--datasetcontrol',
            action='store_true',
            help='Export cycles and datasets data to CSV files.'
        )
        parser.add_argument(
            '--download',
            type=bool,
            help='Enable or disable downloading.'
            )
        parser.add_argument(
            '--status',
            choices=[
                'pending',
                'complete',
                'error',
                'delete',
                'standby',
                'no_file'
                ])
        parser.add_argument(
            '--datasets',
            type=str,
            help='Comma-separated list of dataset codes to update.'
            )
        parser.add_argument(
            '--groups',
            type=str,
            help='Comma-separated list of group IDs to update.'
            )

    def handle(self, *args, **options):
        if options['datasetcontrol']:
            self._perform_datasetcontrol(options)

    def _perform_datasetcontrol(self, options):
        """

        """
        self.stdout.write(
            self.style.SUCCESS(
                'Starting DatasetControl Updating...'
                ))

        try:
            response = update_datasetcontrol_standby(
                datasets=options.get('datasets'),
                groups=options.get('groups'),
                status=options['status'],
                download=options['download']
                )
            self.stdout.write(self.style.SUCCESS(
                response
                ))
        except Exception as e:
            raise CommandError(f"Update failed: {e}")
