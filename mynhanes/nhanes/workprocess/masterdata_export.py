import os
import time
import pandas as pd
from pathlib import Path
from django.conf import settings
from nhanes.models import (
    Cycle,
    Dataset,
    Group,
    SystemConfig,
    WorkProcess,
    WorkProcessMasterData,
    Variable,
    VariableCycle,
    DatasetCycle,
    Field,
    NormalizationRule
)
from nhanes.utils.logs import logger, start_logger


def masterdata_export(folder='masterdata', models_to_export=None):
    """
    Export Master Data in CSV files

    This function exports master data from the database to CSV files
    for deployment.
    The exported data includes SystemConfig, Cycle, Group, and Dataset
    information.

    Returns:
        bool: True if the data export is successful.

    Raises:
        Exception: If there is an error during the data export process.

    custom_models = {
        'custom_cycles.csv': Cycle,
        'custom_datasets.csv': Dataset
    }
    export_masterdata(models_to_export=custom_models)
    """

    # Global Variables
    log_file = __name__
    v_time_start_process = time.time()

    # Start Log monitor
    log = start_logger(log_file)
    logger(log, "s", "Started the Master Data Import")

    try:
        # Setting folder to hosting download files
        base_dir = Path(settings.BASE_DIR) / folder
        os.makedirs(base_dir, exist_ok=True)

        # Use default models if none are specified
        if models_to_export is None:
            models_to_export = {
                'system_config.csv': SystemConfig,
                'cycles.csv': Cycle,
                'groups.csv': Group,
                'datasets.csv': Dataset,
                'variables.csv': Variable,
                'variable_cycles.csv': VariableCycle,
                'dataset_cycles.csv': DatasetCycle,
                'fields.csv': Field,
                'normalization_rules.csv': NormalizationRule,
                'work_processes.csv': WorkProcess,
                'work_process_master_data.csv': WorkProcessMasterData,
            }

        # Iterate over the dictionary and export each model's data to CSV
        for file_name, model in models_to_export.items():
            file_path = base_dir / file_name
            # Query all records from the model
            queryset = model.objects.all()

            if queryset.exists():
                # Convert the queryset to a DataFrame
                df = pd.DataFrame(list(queryset.values()))

                # Handling FK fields
                if 'group_id' in df.columns:
                    df['group'] = df['group_id'].apply(
                        lambda x: Group.objects.get(id=x).group if pd.notna(x) else None)  # noqa E501
                    df = df.drop(columns=['group_id'])
                if 'cycle_id' in df.columns:
                    df['cycle'] = df['cycle_id'].apply(
                        lambda x: Cycle.objects.get(id=x).cycle if pd.notna(x) else None)  # noqa E501
                    df = df.drop(columns=['cycle_id'])
                if 'dataset_id' in df.columns:
                    df['dataset'] = df['dataset_id'].apply(
                        lambda x: Dataset.objects.get(id=x).dataset if pd.notna(x) else None)  # noqa E501
                    df = df.drop(columns=['dataset_id'])
                if 'variable_id' in df.columns:
                    df['variable'] = df['variable_id'].apply(
                        lambda x: Variable.objects.get(id=x).variable if pd.notna(x) else None)  # noqa E501
                    df = df.drop(columns=['variable_id'])

                # Export the DataFrame to CSV
                df.to_csv(file_path, index=False)

            else:
                print(f"No data found for {model.__name__}, skipping export.")

        total_time = time.time() - v_time_start_process
        msm = f"Master Data export completed successfully in {total_time}."
        logger(log, "s", msm)

        return True

    except Exception as e:
        msm = f"An error occurred during the master data export: {str(e)}"
        logger(log, "e", msm)
        return False
