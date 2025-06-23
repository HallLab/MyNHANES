from django.core.management.base import BaseCommand, CommandError
from nhanes.reports import query  # noqa E501


class Command(BaseCommand):
    help = 'Generate a reports from NHANES database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fields_report',
            action='store_true',
            help='Generate a fields report.'
        )
        parser.add_argument(
            '--control_report',
            action='store_true',
            help='Generate a datasets load control report.'
        )
        parser.add_argument(
            '--path',
            type=str,
            help='Specify the path to save the report.'
        )

    def handle(self, *args, **options):

        if options['fields_report']:
            self._perform_fields(options)
        elif options['control_report']:
            self._perform_control(options)
        else:
            self.stdout.write(self.style.WARNING(
                'No action specified. Use --help for options.'
                ))

    def _perform_fields(self, options):
        """
        Perform the fields report generation.

        This method starts the fields report generation process and handles
        any exceptions that occur during the process.
        It calls the `fields_report` function to perform the actual report
        generation.

        Raises:
            CommandError: If the fields report generation fails.

        Returns:
            None
        """
        self.stdout.write(self.style.SUCCESS('Starting Fields Report...'))
        try:
            path = options.get('path', '')
            return_check = query.fields_report(path)
            if return_check:
                self.stdout.write(self.style.SUCCESS(
                    'Fields Report completed successfully.'
                    ))

        except Exception as e:
            raise CommandError(f"Query failed: {e}")

    def _perform_control(self, options):
        """
        Perform the control report generation.

        This method starts the control report generation process and handles
        any exceptions that occur during the process.
        It calls the `control_report` function to perform the actual report
        generation.

        Raises:
            CommandError: If the control report generation fails.

        Returns:
            None
        """
        self.stdout.write(self.style.SUCCESS('Starting Control Report...'))
        try:
            path = options.get('path', '')
            return_check = query.control_report(path)
            if return_check:
                self.stdout.write(self.style.SUCCESS(
                    'Control Report completed successfully.'
                    ))

        except Exception as e:
            raise CommandError(f"Query failed: {e}")
