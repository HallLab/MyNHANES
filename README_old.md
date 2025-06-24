## User Guide: MyNHANES

### Introduction
Welcome to MyNHANES, a powerful tool designed to facilitate the management and analysis of NHANES data. MyNHANES provides an integrated environment to manage master data, work processes, and apply transformations on NHANES datasets. This guide will help you get started with installing MyNHANES, setting up your environment, and using its key features.

### Installation
To install MyNHANES, we recommend using Python 3.12 or above. Follow these steps:

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv mynhanes_env
   source mynhanes_env/bin/activate  # On Windows use `mynhanes_env\Scripts\activate`
   ```

2. **Install MyNHANES via pip**:
   ```bash
   pip install mynhanes
   ```

### Initial Setup
After installation, navigate to the package directory and run the following command to set up the database, create a user, and load the master data and global transformation rules:

```bash
cd path_to_mynhanes_package  # Replace with the actual path
python manage.py deploy --type local
```

This command will initialize the SQLite database and populate it with the necessary data.

### Running the Web Server
Once the setup is complete, you can start the web server to access the MyNHANES system via a web browser:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin` in your web browser to log in and begin using MyNHANES.

### Core Modules

#### Master Data Management
MyNHANES uses master data such as cycles, datasets, variables, and tags to organize NHANES data. These elements are crucial for managing and navigating the data efficiently. 

- **Cycles:** Represent different NHANES survey periods.
- **Datasets:** Collections of data for each cycle.
- **Variables:** Individual variables within the datasets.
- **Tags:** Used to categorize and filter datasets and variables.

#### WorkProcess
The WorkProcess module manages the lifecycle of datasets, from downloading to processing. 

- **Activating a Dataset:** In the admin interface, you can activate datasets for download by setting their status and managing their lifecycle.
- **Ingestion:** Once a dataset is activated, you can ingest the data into the system for further analysis.

#### Transformations
Transformations allow you to apply predefined rules to the NHANES data, modifying or normalizing it for analysis.

- **Running Transformations:** Transformations can be triggered through the admin interface, where you select the relevant rules to apply to the data.
- **Custom Rules:** You can create and manage custom transformation rules based on your analytical needs.

### Queries and Data Export
MyNHANES provides tools for creating dynamic queries and exporting the results.

- **Query Builder:** Use the query builder to define custom queries across cycles, datasets, and variables.
- **Data Export:** Export query results to CSV or other formats directly from the admin interface.

### Storage
MyNHANES uses SQLite as the default database for storing all data, which makes it easy to manage and share data files.

