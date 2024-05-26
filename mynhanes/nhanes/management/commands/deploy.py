from django.core.management.base import BaseCommand, CommandError
from nhanes.services.deploy import export_data_to_deploy, import_data_to_deploy, deploy  # noqa E501


class Command(BaseCommand):
    help = 'Executes deployment operations for the NHANES project.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export cycles and datasets data to CSV files.'
        )
        parser.add_argument(
            '--import',
            action='store_true',
            help='Import cycles and datasets data from CSV files.'
        )
        parser.add_argument(
            '--deploy',
            choices=['local', 'remote'],
            help='Deploy the application either locally or remotely.'
        )
        parser.add_argument(
            '--path',
            type=str,
            help='Specify the path for deployment when using remote option.'
        )

    def handle(self, *args, **options):
        if options['export']:
            self._perform_export()
        elif options['import']:
            self._perform_import()
        elif options['deploy']:
            self._perform_deploy(options)
        else:
            self.stdout.write(self.style.WARNING(
                'No action specified. Use --help for options.'
                ))

    def _perform_export(self):
        """
        Performs the data export process.

        This method initiates the data export process and handles any
        exceptions that may occur.
        It calls the `export_data_to_deploy` function to perform the
        actual export.

        Raises:
            CommandError: If the data export fails.

        """
        self.stdout.write(self.style.SUCCESS('Starting data export...'))
        try:
            export_data_to_deploy()
            self.stdout.write(self.style.SUCCESS(
                'Data export completed successfully.'
                ))
        except Exception as e:
            raise CommandError(f"Data export failed: {e}")

    def _perform_import(self):
        """
        Performs the data import process.

        This method starts the data import process and handles any exceptions
        that occur during the import.
        It calls the `import_data_to_deploy` function to perform the actual
        import.

        Raises:
            CommandError: If the data import fails.

        Returns:
            None
        """
        self.stdout.write(self.style.SUCCESS('Starting data import...'))
        try:
            import_data_to_deploy()
            self.stdout.write(
                self.style.SUCCESS('Data import completed successfully.')
                )
        except Exception as e:
            raise CommandError(f"Data import failed: {e}")

    def _perform_deploy(self, options):
        """
        Perform the deployment based on the provided options.

        Args:
            options (dict): A dictionary containing the deployment options.

        Raises:
            CommandError: If the deployment fails.

        Returns:
            None
        """
        deploy_option = options['deploy']
        deploy_path = options.get('path', '')  # Empty string if not provided
        self.stdout.write(self.style.SUCCESS(
            f'Starting {deploy_option} deployment...'
        ))
        try:
            deploy(deploy_option, deploy_path)
            self.stdout.write(self.style.SUCCESS(
                'Deployment completed successfully.'
            ))
        except Exception as e:
            raise CommandError(f"Deployment failed: {e}")
