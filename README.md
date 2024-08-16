# MyNHANES

## Overview
MyNHANES is a Django-based application designed to manage and analyze the NHANES (National Health and Nutrition Examination Survey) dataset. It provides a suite of tools for importing, exporting, querying, and managing NHANES data, enabling users to perform complex data analyses and generate reports efficiently.

## Features
- **Data Management**: Import and export NHANES cycles, datasets, and configurations seamlessly between development and production environments.
- **Custom Queries**: Users can configure custom queries with dynamic fields and filters to extract specific data from the NHANES dataset.
- **Automated Deployment**: Supports automated setup and deployment processes, making it easy to get the application running in any environment.
- **User-Friendly Interface**: Comes with an intuitive admin interface for managing NHANES data and configurations without needing direct database access.

## Installation
To install MyNHANES, follow these steps:

1. Ensure you have Python 3.10 or newer installed.
2. Install the package using pip:

    ```bash
    pip install mynhanes
    ```

3. After installation, you can start setting up your application with the available management commands.

## Usage
Once installed, you can use the management commands provided by Django to manage your NHANES data:

- **Deploying the Application**:
    ```bash
    python manage.py deploy --option [local|remote]
    ```
    Use `local` for a fresh setup and `remote` to connect to an existing database.

- **Start Web Interface**:
    ```bash
    python manage.py runserver
    ```
    This command will start a local web server.

- **Importing Data**:
    ```bash
    python manage.py loader
    ```
    Use this command will load data from NHANES.

## Configuration
Edit the `settings.py` file to adjust database configurations and other settings according to your environment needs.

## Contributing
Contributions to MyNHANES are welcome! Please feel free to fork the repository, make changes, and submit pull requests.

## License
MyNHANES is open-source software licensed under the MIT license.
