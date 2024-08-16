from django.core.management.base import BaseCommand, CommandError
from nhanes.services.deploy import deploy  # noqa E501


class Command(BaseCommand):
    help = 'Executes deployment operations for the NHANES project.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['local', 'remote'],
            help='Deploy the application either locally or remotely.'
        )
        parser.add_argument(
            '--path',
            type=str,
            help='Specify the path for deployment when using remote option.'
        )

    def handle(self, *args, **options):
        if options['type']:
            self._perform_deploy(options)
        else:
            self.stdout.write(self.style.WARNING(
                'No action specified. Use --help for options.'
                ))

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
        deploy_option = options['type']
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
