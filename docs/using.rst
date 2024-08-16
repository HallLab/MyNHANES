Usage
=====

Starting the Application
------------------------

After installing MyNHANES, you can start the application using the following command:

.. code-block:: bash

    python manage.py runserver

This will initiate the Django server, making the application accessible via the specified port, typically at `http://localhost:8000`.

Navigating the Admin Panel
--------------------------

To access the administrative panel, navigate to:

.. code-block:: none

    http://localhost:8000/admin

Here you can login with the user credentials created during the deployment phase.

.. image:: /_static/pictures/admin_login.png
    :alt: Login page of the MyNHANES admin panel

Data Management
---------------

**Initial Data Setup:**

When you execute the deployment with the local setting, the application sets up a new SQLite database filled with master data necessary for NHANES operations such as Cycles, Groups, and Datasets.

.. image:: /_static/pictures/first_page.png
    :alt: Initial data setup in MyNHANES

**Loading NHANES Data:**

The bulk of NHANES data needs to be loaded into the system to perform meaningful queries and analysis. Here’s how you manage this data:

1. **Cycle Management:** Manage different NHANES cycles like 1999-2000, 2001-2002 etc., through the `Cycle` table. This is crucial for segmenting the data loads according to specific time frames.

.. image:: /_static/pictures/cycle.png
    :alt: Cycle data

2. **Group Management:** NHANES data is categorized into different groups such as Demographics, Examination, Laboratory, and Questionnaire. The `Group` table allows you to manage these categorizations.

.. image:: /_static/pictures/group.png
    :alt: Group data

3. **Dataset Management:** Specific datasets like Demographic Data, Examination Data etc., are managed in the `Dataset` table. Each dataset corresponds to a particular group.

.. image:: /_static/pictures/dataset.png
    :alt: Dataset data

4. **Field Management:** Detailed data fields within each dataset are managed through the `Field` table. Fields are consistent across cycles but can be grouped differently in reports.

.. image:: /_static/pictures/field.png
    :alt: Field data

.. image:: /_static/pictures/field_cycle.png
    :alt: Field by Cycle data

5. **Download Control:** This functionality manages the downloading and integration of NHANES data into the database. Each dataset by cycle will have its status managed here, where you can set datasets to be downloaded and integrated.

.. image:: /_static/pictures/dataset_control.png
    :alt: Dataset Control data

6. **System Configuration:** System configurations determine how datasets are processed and loaded. For example, `auto_create_dataset_control` setting in `SystemConfig` determines whether dataset controls should be automatically created for new datasets or cycles.

.. image:: /_static/pictures/system.png
    :alt: System Configs data

7. **Data Table:** The `Data` table stores all the loaded NHANES data, potentially becoming a very large table depending on the volume of loaded data.

.. image:: /_static/pictures/data.png
    :alt: Data

Querying and Reporting
----------------------

**Query Structure Table:**

The `Query Structure` table allows users to define custom queries and reports. Users can specify which fields (like cycle, dataset, group) to include in the output and apply various filters to refine the data.

.. image:: /_static/pictures/query_01.png
    :alt: Query Structure created in MyNHANES

.. image:: /_static/pictures/query_02.png
    :alt: Setting Query Structure

.. image:: /_static/pictures/query_03.png
    :alt: Download query results

.. image:: /_static/pictures/report.png
    :alt: CSV file from query results

To generate reports, select the desired query structure and export the results to a CSV file by clicking the export button in the admin panel.


TO DO:
- Add the options to donwloads (csv, db or both)