import os
import time
import pandas as pd
import requests
from pathlib import Path
from io import StringIO
from django.db import transaction
from nhanes.models import (
    Version,
    Cycle,
    Dataset,
    Group,
    WorkProcessMasterData,
    Variable,
    VariableCycle,
    DatasetCycle,
    Rule,
    QueryColumns,
)
from nhanes.utils.logs import logger, start_logger
from django.utils import timezone
from nhanes.workprocess.sync_workprocess import check_and_sync_workprocess
from core.parameters import config


def _get_data(BASE_URL, file_name, log):
    """
    Retrieves data from a CSV file either from a GitHub URL or a local directory.

    Parameters:
        BASE_URL (str): The base URL or directory path.
        file_name (str): The name of the CSV file.
        log (str): The log message.

    Returns:
        pandas.DataFrame or None: The DataFrame containing the data from the CSV file,
        or None if an error occurred.
    """
    try:
        # read data from CSV file
        if "https://raw.githubusercontent.com/" in BASE_URL:
            # Read from GitHub
            response = requests.get(BASE_URL + file_name)
            response.raise_for_status()
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)

        elif os.path.isdir(BASE_URL):
            # Read from local directory
            file_path = Path(BASE_URL) / file_name
            if file_path.exists():
                df = pd.read_csv(file_path)
            else:
                msm = f"There are not file on: {file_name}"
                logger(log, "e", msm)
                return None
        else:
            msm = f"BASE_URL isn't a valid Github or Path: {BASE_URL}"
            logger(log, "e", msm)
            return None

        df = df.dropna(subset=['id'])
        return df

    except (requests.exceptions.RequestException, FileNotFoundError, ValueError) as e:
        msm = f"Error when try got the file: {e}"
        logger(log, "e", msm)
        return None


def _initialize_workprocess_master_data(log, BASE_URL):
    """
    Initializes the WorkProcessMasterData by fetching data from a CSV file and creating
    model instances.

    Args:
        log (Logger): The logger object for logging messages.
        BASE_URL (str): The base URL for fetching the CSV file.

    Returns:
        QuerySet: The QuerySet of WorkProcessMasterData objects.

    Raises:
        None

    """
    # get all WorkProcessMasterData
    qs_wp = WorkProcessMasterData.objects.all()
    # if new base, create the WorkProcessMasterData
    # if not qs_wp.exists():
    df = _get_data(BASE_URL, 'work_process_master_data.csv', log)
    if df is not None:
        model_instances = [
            WorkProcessMasterData(
                component_type=record.component_type,
                source_file_version=record.source_file_version,
                status="pending",
            )
            for record in df.itertuples()
        ]
        WorkProcessMasterData.objects.bulk_create(
            model_instances,
            ignore_conflicts=True
        )
        qs_wp = WorkProcessMasterData.objects.all()
        logger(
            log,
            "s",
            "Started WorkProcessMasterData",
            content_object=qs_wp.first()
            )
    else:
        logger(log, "e", "Failed to load WorkProcessMasterData from CSV")
    return qs_wp


def masterdata_import():
    """
    Imports master data from specified URLs and populates the database with the data.

    This function performs the following steps:
    1. Retrieves the master data repository URL from the system configuration.
    2. Initializes the work process for master data import.
    3. Iterates over each file in the MODELS_TO_FILES dictionary.
    4. Retrieves the data from the specified URL for each file.
    5. Inserts the data into the corresponding model in the database.
    6. Updates the work process status and last synced time.

    Returns:
        None
    """

    # start Log monitor
    log_file = __name__
    v_time_start_process = time.time()
    log = start_logger(log_file)
    logger(log, "s", "Started the Master Data Import")

    # check repository of masterdata
    BASE_URL = config['workprocess']['masterdata_repository']

    # define paramets to import
    MODELS_TO_FILES = {
        'versions.csv': (Version, 'version'),
        'cycles.csv': (Cycle, 'cycle'),
        'groups.csv': (Group, 'group'),
        'datasets.csv': (Dataset, 'dataset'),
        'variables.csv': (Variable, 'variable'),
        'variable_cycles.csv': (VariableCycle, ['variable', 'cycle']),
        'dataset_cycles.csv': (DatasetCycle, ['dataset', 'cycle']),
        'rules.csv': (Rule, ['rule', 'version']),
        'query_columns.csv': (QueryColumns, ['column_name']),
    }

    # call the function that initializes the WorkProcessMasterData
    qs_wp = _initialize_workprocess_master_data(log, BASE_URL)

    try:
        for file_name, (model, unique_fields) in MODELS_TO_FILES.items():

            df = _get_data(BASE_URL, file_name, log)

            if df is None:
                continue

            df = df.drop(columns=['id'])
            df = df.fillna("")

            try:
                qry_wp = qs_wp.get(component_type=model.__name__)
            except WorkProcessMasterData.DoesNotExist:
                logger(
                    log,
                    "e",
                    f"WorkProcessMasterData not found for {model.__name__}"
                )
                continue

            # Insert data into the database
            with transaction.atomic():
                for _, row in df.iterrows():
                    if isinstance(unique_fields, list):
                        filter_kwargs = {field: row[field] for field in unique_fields}
                    else:
                        filter_kwargs = {unique_fields: row[unique_fields]}

                    if file_name == "datasets.csv":
                        if not model.objects.filter(**filter_kwargs).exists():
                            group = Group.objects.get(group=row['group'])
                            model.objects.create(
                                dataset=row['dataset'],
                                description=row['description'],
                                group=group)

                    elif file_name == "dataset_cycles.csv":
                        if not model.objects.filter(
                            dataset_id__dataset=filter_kwargs['dataset'],
                            cycle_id__cycle=filter_kwargs['cycle']
                        ).exists():
                            cycle = Cycle.objects.get(cycle=row['cycle'])
                            dataset = Dataset.objects.get(dataset=row['dataset'])
                            model.objects.create(
                                cycle=cycle,
                                dataset=dataset,
                                metadata_url=row['metadata_url'],
                                description=row['description'] if pd.notna(row['description']) else None,  # noqa E501 
                                has_special_year_code=row['has_special_year_code'],
                                special_year_code=row['special_year_code'],
                                has_dataset=row['has_dataset']
                                )

                    elif file_name == "variable_cycles.csv":
                        if not model.objects.filter(
                            variable_id__variable=filter_kwargs['variable'],
                            cycle_id__cycle=filter_kwargs['cycle'],
                            # version_id__version=filter_kwargs['version']
                            version_id__version='nhanes'

                        ).exists():
                            cycle = Cycle.objects.get(cycle=row['cycle'])
                            dataset = Dataset.objects.get(dataset=row['dataset'])
                            variable = Variable.objects.get(variable=row['variable'])
                            version = Version.objects.get(version='nhanes')
                            model.objects.create(
                                version=version,
                                cycle=cycle,
                                dataset=dataset,
                                variable=variable,
                                variable_name=row['variable_name'],
                                sas_label=row['sas_label'],
                                english_text=row['english_text'],
                                target=row['target'],
                                type=row['type'],
                                value_table=row['value_table']
                                )
                    # Process others models with no FK
                    else:
                        if not model.objects.filter(**filter_kwargs).exists():
                            model.objects.create(**row.to_dict())

            # sync workprocess model
            if file_name == "dataset_cycles.csv":
                import_success = check_and_sync_workprocess()
                if import_success:
                    logger(log, "s", "Workprocess model sync successfully")
                else:
                    logger(log, "e", "Workprocess model sync failed")

            qry_wp.status = "complete"
            qry_wp.last_synced_at = timezone.now()
            qry_wp.save()

    except Exception as e:
        qry_wp.status = "error"
        qry_wp.last_synced_at = timezone.now()
        qry_wp.save()
        logger(log, "e", f"Error: {e}")
        return False

    total_time = time.time() - v_time_start_process
    logger(
        log,
        "s",
        f"The Master Data was imported in {total_time}"
    )
    return True
