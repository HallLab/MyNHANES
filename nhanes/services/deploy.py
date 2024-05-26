import os
import re
import pandas as pd
from pathlib import Path
from django.conf import settings
from nhanes.models import Cycle, Dataset, Group, DatasetControl, SystemConfig
from django.core.management import call_command
from django.db import transaction


def export_data_to_deploy():
    """
    Export data to deploy.

    This function exports various data from the database to CSV files
    for deployment.
    The exported data includes SystemConfig, Cycle, Group, and Dataset
    information.

    Returns:
        bool: True if the data export is successful.

    Raises:
        Exception: If there is an error during the data export process.
    """
    try:
        # setting folder to hosting download files
        base_dir = Path(settings.BASE_DIR) / 'deploy'
        os.makedirs(base_dir, exist_ok=True)

        # Export SystemConfig
        sysconfig = SystemConfig.objects.all()
        sysconfig_df = pd.DataFrame(list(sysconfig.values()))
        sysconfig_df.to_csv(str(base_dir / 'systemconfig.csv'), index=False)
        print("  System configuration data exported successfully.")

        # Export Cycle
        cycles = Cycle.objects.all()
        cycles_df = pd.DataFrame(list(cycles.values()))
        cycles_df.to_csv(str(base_dir / 'cycles.csv'), index=False)
        print("  Cycles data exported successfully.")

        # Export Group
        groups = Group.objects.all()
        groups_df = pd.DataFrame(list(groups.values(
            'id',
            'group',
            'description'
            )))
        groups_df.to_csv(str(base_dir / 'groups.csv'), index=False)
        print("  Groups data exported successfully.")

        # Export Dataset including Group data
        datasets = Dataset.objects.select_related('group').all()
        datasets_df = pd.DataFrame.from_records(
            [
                {
                    'dataset_id': ds.id,
                    'name': ds.dataset,
                    'description': ds.description,
                    'group_id': ds.group.id,
                    # 'group_name': ds.group.group
                }
                for ds in datasets
            ]
        )
        datasets_df.to_csv(str(base_dir / 'datasets.csv'), index=False)
        print("  Exported Datasets data successfully.")

    except Exception as e:
        print(f"Failed to export data: {e}")
        raise
    return True


def import_data_to_deploy():
    """
    Imports data for deployment.

    This function sets up the necessary folders for hosting download files,
    loads system configuration, cycles, groups, and datasets, and prints a
    completion message if successful.

    Returns:
        bool: True if the data import is successful, False otherwise.
    """
    try:
        # setting folder to hosting download files
        base_dir = Path(settings.BASE_DIR) / 'deploy'
        os.makedirs(base_dir, exist_ok=True)

        _load_systemconfig(base_dir)
        _load_cycles(base_dir)
        _load_groups(base_dir)
        _load_datasets(base_dir)
        print("Data load completed!")
        return True
    except Exception as e:
        print(f"Failed to import data: {e}")
        return False


def _load_systemconfig(base_dir):
    """
    Load system configuration data from a CSV file and update or
    create SystemConfig objects.

    Parameters:
    - base_dir (str): The base directory where the CSV file is located.

    Raises:
    - FileNotFoundError: If the system configuration file is not found.
    - Exception: If there is an error loading the system configuration data.

    Returns:
    None
    """
    file_path = Path(base_dir) / 'systemconfig.csv'
    try:
        data = pd.read_csv(file_path)
        for index, row in data.iterrows():
            SystemConfig.objects.update_or_create(
                config_key=row['config_key'],
                defaults={
                    'config_value': row['config_value']
                }
            )
        print("System configuration data loaded successfully.")
    except FileNotFoundError:
        print("System configuration file not found.")
    except Exception as e:
        print(f"Error loading system configuration data: {e}")


def _load_cycles(base_dir):
    """
    Load cycles data from a CSV file and update or create Cycle objects
    in the database.

    Parameters:
    - base_dir (str): The base directory where the CSV file is located.

    Raises:
    - FileNotFoundError: If the CSV file is not found.
    - Exception: If there is an error loading the Cycle data.

    Returns:
    - None
    """
    file_path = base_dir / 'cycles.csv'
    try:
        data = pd.read_csv(file_path)
        for index, row in data.iterrows():
            Cycle.objects.update_or_create(
                id=row['id'],
                defaults={
                    'cycle': row['cycle'],
                    'base_dir': row['base_dir'],
                    'year_code': row['year_code'],
                    'base_url': row['base_url'],
                    'dataset_url_pattern': row['dataset_url_pattern']
                }
            )
        print("Cycles data loaded successfully.")
    except FileNotFoundError:
        print("Cycle file not found.")
    except Exception as e:
        print(f"Error loading Cycle data: {e}")


def _load_groups(base_dir):
    """
    Load group data from a CSV file and update or create Group
    objects in the database.

    Args:
        base_dir (str): The base directory path where the CSV file is located.

    Raises:
        FileNotFoundError: If the CSV file is not found.
        Exception: If there is an error loading the group data.

    Returns:
        None
    """
    file_path = base_dir / 'groups.csv'
    try:
        data = pd.read_csv(file_path)
        for index, row in data.iterrows():
            Group.objects.update_or_create(
                id=row['id'],
                defaults={
                    'group': row['group'],
                    'description': row['description']
                }
            )
        print("Group data loaded successfully.")
    except FileNotFoundError:
        print("Group file not found.")
    except Exception as e:
        print(f"Error loading Group data: {e}")


def _load_datasets(base_dir):
    """
    Load datasets from a CSV file and update or create corresponding
    Dataset objects.

    Args:
        base_dir (str): The base directory path where the CSV file is located.

    Raises:
        FileNotFoundError: If the dataset file is not found.
        Exception: If there is an error loading the dataset data.

    Returns:
        None
    """
    file_path = base_dir / 'datasets.csv'
    try:
        data = pd.read_csv(file_path)

        with transaction.atomic():
            for index, row in data.iterrows():
                # group = Group.objects.get(id=row['group_id'])
                dataset, created = Dataset.objects.update_or_create(
                    id=row['dataset_id'],
                    defaults={
                        'dataset': row['name'],
                        'description': row['description'],
                        'group_id': row['group_id']
                    }
                )
            print("Dataset data loaded successfully.")

            auto_create = SystemConfig.objects.filter(
                config_key='auto_create_dataset_controls'
                ).first()

            if auto_create and str(auto_create.config_value).lower() == 'true':
                _create_dataset_controls()

    except FileNotFoundError:
        print("Dataset file not found.")
    except Exception as e:
        print(f"Error loading Dataset data: {e}")


def _create_dataset_controls():
    """
    Creates DatasetControl objects for all combinations of datasets and cycles.

    This function retrieves all datasets and cycles from the database and
    creates a DatasetControl object
    for each combination of dataset and cycle. The DatasetControl object
    is created with a default status
    of 'standby'.

    Returns:
        None
    """
    try:
        datasets = Dataset.objects.all()
        cycles = Cycle.objects.all()
    except Exception as e:
        print(f"Error getting datasets and cycles: {e}")

    try:
        for dataset in datasets:
            for cycle in cycles:
                DatasetControl.objects.get_or_create(
                    dataset=dataset,
                    cycle=cycle,
                    defaults={
                        'status': 'standby'  # Status inicial
                    }
                )
        # print("DatasetControls created for all cycles.")
    except Exception as e:
        print(f"Error to create DataControl data: {e}")


def deploy(deploy_option, deploy_path=''):
    """
    Deploys the application based on the specified deploy_option.

    Args:
        deploy_option (str): The deployment option. Valid options
        are 'local' or 'remote'.
        deploy_path (str, optional): The path for remote deployment.
        Defaults to ''.

    Returns:
        bool: True if the deployment is successful, False otherwise.
    """
    if deploy_option == 'local':
        print("Running migrations...")
        call_command('makemigrations')
        call_command('migrate')
        # os.system('python manage.py makemigrations')
        # os.system('python manage.py migrate')

        print("Creating superuser...")
        call_command('createsuperuser')
        # os.system('python manage.py createsuperuser')

        print("Importing data...")
        import_data_to_deploy()
        return True

    elif deploy_option == 'remote':
        print("Setting up remote database configuration...")
        if deploy_path:
            _update_database_settings(deploy_path)
            print(f"Database path set to {deploy_path}")
        else:
            print("No path provided for remote deployment. Please specify a valid path.")  # noqa
            return False

        return True

    else:
        print("Invalid deploy option provided. Please choose 'local' or 'remote'.")  # noqa
        return False


def _update_database_settings(db_path):
    """
    Update the database settings in the project's settings.py file.

    Args:
        db_path (str): The new path to the database file.

    Returns:
        None

    Raises:
        None
    """
    settings_path = Path(settings.BASE_DIR) / 'project' / 'settings.py'
    new_db_config = f"""'{db_path}'"""

    with open(settings_path, 'r') as file:
        content = file.read()

    content = re.sub(
        # r"(DATABASES\s*=\s*\{.*?\})",
        r"(BASE_DIR / 'db.sqlite3')",
        new_db_config,
        content,
        flags=re.DOTALL
    )

    with open(settings_path, 'w') as file:
        file.write(content)

    print("Database settings updated successfully.")
