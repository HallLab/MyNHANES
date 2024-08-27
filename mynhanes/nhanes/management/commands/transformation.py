from django.core.management.base import BaseCommand
from nhanes.workprocess.transformation_manager import TransformationManager


# class Command(BaseCommand):
#     help = 'Aplica todas as regras de normalização nos dados brutos'

#     def handle(self, *args, **kwargs):
#         manager = TransformationManager()
#         manager.apply_transformations()
#         self.stdout.write(self.style.SUCCESS('Transformações aplicadas com sucesso'))


class Command(BaseCommand):
    help = 'apply transformations rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rules',
            nargs='*',
            type=str,
            help='List of rules to be applied. If omitted, all active rules will be processed.' # noqa E501
        )

    def handle(self, *args, **options):
        rules = options['rules']

        manager = TransformationManager(rules=rules)
        manager.apply_transformation()

        self.stdout.write(self.style.SUCCESS('Transformações aplicadas com sucesso'))
