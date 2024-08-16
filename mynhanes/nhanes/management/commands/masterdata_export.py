from django.core.management.base import BaseCommand
from nhanes.workprocess.masterdata_export import masterdata_export

"""
Export Master Data to CSV files

Usage:
python manage.py masterdata_export [--folder FOLDER] [--models MODELS [MODELS ...]]

Options:
--folder FOLDER
    The folder where CSV files will be saved. Default is 'masterdata'.
--models MODELS [MODELS ...]
    List of model names to export. Specify the names of the models you want to export,
    separated by spaces. Available models:
    - SystemConfig
    - Cycle
    - Group
    - Dataset
    - Variable
    - VariableCycle
    - DatasetCycle
    - Field
    - NormalizationRule
    - WorkProcess
    - WorkProcessMasterData
    If no models are specified, all models will be exported.

Example:
$ python manage.py export_masterdata --folder my_export_folder --models Cycle Group
"""


class Command(BaseCommand):
    help = 'Export Master Data to CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            default='masterdata',
            help='The folder where CSV files will be saved'
        )
        parser.add_argument(
            '--models',
            nargs='+',
            type=str,
            help='List of model names to export (e.g., Cycle Dataset Group)'
        )

    def handle(self, *args, **options):
        folder = options['folder']
        models = options['models']

        # if models is not None, convert them to the expected format
        if models:
            available_models = {
                'SystemConfig': 'system_config.csv',
                'Cycle': 'cycles.csv',
                'Group': 'groups.csv',
                'Dataset': 'datasets.csv',
                'Variable': 'variables.csv',
                'VariableCycle': 'variable_cycles.csv',
                'DatasetCycle': 'dataset_cycles.csv',
                'Field': 'fields.csv',
                'NormalizationRule': 'normalization_rules.csv',
                'WorkProcess': 'work_processes.csv',
                'WorkProcessMasterData': 'work_process_master_data.csv',
            }

            models_to_export = {
                available_models[model]: globals()[model] for model in models if model in available_models  # noqa E501
            }

        else:
            models_to_export = None  # export all models

        # call the export_masterdata function with the appropriate parameters
        export_success = masterdata_export(
            folder=folder,
            models_to_export=models_to_export
        )

        if export_success:
            self.stdout.write(self.style.SUCCESS(
                'Master Data export completed successfully')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Master Data export failed')
            )
