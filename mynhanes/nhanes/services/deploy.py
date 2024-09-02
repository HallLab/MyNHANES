import re
from pathlib import Path
from django.conf import settings
from django.core.management import call_command
from nhanes.workprocess.masterdata_import import masterdata_import
# from nhanes.workprocess.sync_workprocess import (
#     check_and_sync_datasetcycle,
#     check_and_sync_workprocess
#     )


def deploy(deploy_option, deploy_path=''):

    # no logs because this is a script to deploy the db
    if deploy_option == 'local':
        print("Running migrations...")
        call_command('makemigrations')
        call_command('migrate')

        print("Creating superuser...")
        call_command('createsuperuser')

        print("Importing Master Data...")
        check_return = masterdata_import()
        # check_return = check_and_sync_datasetcycle()
        # check_return = check_and_sync_workprocess()

        if check_return:
            return True

    elif deploy_option == 'remote':
        # remote deployment requires a valid path to the database file
        # no import of master data, presumably already done
        print("Setting up remote database configuration...")
        if deploy_path:
            check_return = _update_database_settings(deploy_path)
            if not check_return:
                return False
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
    try:
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
        return True

    except Exception as e:
        print(f"Error updating database settings: {e}")
        return False
