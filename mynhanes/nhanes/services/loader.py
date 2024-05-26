import os
import requests
from io import StringIO
from time import sleep
import string
import numpy as np
import pandas as pd
from pathlib import Path
import pyreadstat
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from nhanes.models import Field, FieldCycle, Dataset, Cycle, Data, DatasetControl, SystemConfig # noqa E501


class EmptySectionError(Exception):
    pass


def _get_data_from_xpt(datafile):
    """
    Reads data from an XPT file and returns a DataFrame and metadata.

    Parameters:
    datafile (str): The path to the XPT file.

    Returns:
    df (pandas.DataFrame): The data read from the XPT file.
    df_metadata (pandas.DataFrame): The metadata of the variables
    in the XPT file.

    """
    try:
        df, meta = pyreadstat.read_xport(datafile)
    except Exception as e:
        print(f"Error reading XPT file: {e}")

    df = df.astype({'SEQN': int})
    df = df.set_index('SEQN')

    # List to store metadata of all variables
    all_metadata = []

    # Iterate over all variables
    for var_name in meta.column_names:
        # Get specific metadata for each variable
        variable_labels = meta.column_names_to_labels.get(var_name, "")
        variable_measurements = meta.readstat_variable_types.get(
            var_name,
            None
            )

        # Create a dictionary with relevant metadata
        metadata_dict = {
            'Variable': var_name,
            'Type': variable_measurements,
            'Labels': variable_labels,
        }
        all_metadata.append(metadata_dict)

    # Convert the list of dictionaries into a DataFrame
    df_metadata = pd.DataFrame(all_metadata)

    return df, df_metadata


def _parse_html_variable_info_section(info):
    """
    Parses the HTML variable info section and returns a dictionary with the
    parsed information.

    Args:
        info (BeautifulSoup): The BeautifulSoup object representing the HTML
        variable info section.

    Returns:
        dict: A dictionary containing the parsed information from the HTML
        variable info section.
    """
    infodict = {
        i[0].text.strip(': ').replace(' ', ''): i[1].text.strip()
        for i in zip(info.find_all('dt'), info.find_all('dd'))
    }
    # TODO: Check if this field is necessary
    infodict['VariableNameLong'] = ''.join([i.title() for i in infodict['SASLabel'].translate(str.maketrans('', '', string.punctuation)).split(' ')]) if 'SASLabel' in infodict else infodict['VariableName'] # noqa E501

    return infodict


def _parse_html_variable_section(
        source_code,
        section,
        variable_df,
        code_table,
        ):
    """
    Parses the HTML variable section and extracts information about the
    variables.

    Args:
        source_code (str): The source code of the HTML page.
        section (BeautifulSoup): The BeautifulSoup object representing the
        variable section.
        variable_df (pandas.DataFrame): The DataFrame to store the variable
        information.
        code_table (dict): The dictionary to store the code tables.

    Returns:
        tuple: A tuple containing the updated variable DataFrame and code
        table dictionary.
    """
    title = section.find('h3', {'class': 'vartitle'})

    if title is None or title.text.find('CHECK ITEM') > -1:
        raise EmptySectionError

    info = section.find('dl')

    infodict = _parse_html_variable_info_section(info)
    assert title.get('id') == infodict['VariableName']

    infodict['VariableName'] = infodict['VariableName'].upper()
    index_variable = 'VariableName'
    infodict['index'] = infodict[index_variable]

    for key in infodict:
        if key != 'index':
            variable_df.loc[infodict[index_variable], key] = infodict[key]

    table = section.find('table')
    if table is not None:
        table_string = str(table)
        # parsing the table to a string and then to a StringIO object
        table_io = StringIO(table_string)

        # read the table with pandas
        infotable = pd.read_html(table_io)[0]

        code_table[infodict['index']] = infotable

    variable_df['Source'] = source_code

    return variable_df, code_table


def _parse_nhanes_html_docfile(source_code, docfile):
    """
    Parses the NHANES HTML documentation file and extracts variable
    information.

    Args:
        source_code (str): The source code of the NHANES dataset.
        docfile (str): The path to the HTML documentation file.

    Returns:
        tuple: A tuple containing two elements:
            - variable_df (pandas.DataFrame): A DataFrame containing the
            parsed variable information.
            - code_table (dict): A dictionary containing the parsed code table
            information.
    """
    variable_df = pd.DataFrame()
    code_table = {}

    try:
        with open(docfile, 'r') as f:
            soup = BeautifulSoup('\n'.join(f.readlines()), 'html.parser')

        # each variable is described in a separate div
        for section in soup.find_all('div'):
            try:
                variable_df, code_table = _parse_html_variable_section(
                    source_code, section, variable_df, code_table)
            except EmptySectionError:
                pass

        variable_df = variable_df.loc[
            variable_df.index != 'SEQN_%s' % source_code, :
            ]
        variable_df.index = variable_df.VariableName + '_' + variable_df.Source

        return variable_df, code_table
    except Exception as e:
        print(f"Error parsing HTML documentation file: {e}")
        return variable_df, code_table


def _get_data_from_htm(doc_code, docfile):
    """
    Parses an HTML document file and extracts variable data and code tables.

    Args:
        doc_code (str): The code associated with the document.
        docfile (str): The path to the HTML document file.

    Returns:
        tuple: A tuple containing the variable data DataFrame and the code
        tables dictionary.
    """
    variable_dfs = {}
    code_table = {}
    variable_df = None

    # print('parsing docfile', docfile)

    variable_dfs[doc_code], code_tables = _parse_nhanes_html_docfile(
        doc_code,
        docfile
    )

    # TODO: Check if this works when set to No Metadata
    if not code_tables:
        return variable_df, code_table

    code_table.update(code_tables)

    for code in variable_dfs:
        if variable_df is None:
            variable_df = variable_dfs[code]
        else:
            variable_df = pd.concat((variable_df, variable_dfs[code]))
    return variable_df, code_table


def process_and_save_metadata(df, dataset_id, cycle_id, load_metadata=True):
    """
    Process and save metadata from a DataFrame to the database.

    Args:
        df (pandas.DataFrame): The DataFrame containing the metadata.
        dataset_id (int): The ID of the dataset.
        cycle_id (int): The ID of the cycle.
        load_metadata (bool, optional): Whether to load metadata or not.
        Defaults to True.

    Returns:
        bool: True if the metadata processing and saving is successful.

    Raises:
        ObjectDoesNotExist: If the dataset or cycle does not exist.
        IntegrityError: If there is a database error while processing the
        metadata.
        Exception: If an unexpected error occurs.

    """
    try:
        # dataset = Dataset.objects.get(id=dataset_id)
        cycle = Cycle.objects.get(id=cycle_id)
    except ObjectDoesNotExist as e:
        print(f"Error: {e}")
        return

    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                field, created = Field.objects.get_or_create(
                    field=row['VariableName'],
                    defaults={
                        'internal_id': row['VariableName'],
                        'description': row['SASLabel']
                    }
                )

                if load_metadata:
                    field_m, create_m = FieldCycle.objects.update_or_create(
                        field=field,
                        cycle=cycle,
                        defaults={
                            'variable_name': row['VariableName'],
                            'sas_label': row['SASLabel'],
                            'english_text': row['EnglishText'],
                            'target': row['Target'],
                            'type': row['Type'],
                            'value_table': row['CodeTables']
                        }
                    )
                else:
                    field_m, create_m = FieldCycle.objects.update_or_create(
                        field=field,
                        cycle=cycle,
                        defaults={
                            'variable_name': row['VariableName'],
                            'sas_label': row['SASLabel'],
                            'english_text': '',
                            'target': '',
                            'type': row['Type'],
                            'value_table': ''
                        }
                    )
                print(f"Processed {field.field} with status {'created' if created else 'updated'}.") # noqa E501
            except IntegrityError as e:
                print(f"Database error while processing {row['VariableName']}: {e}") # noqa E501
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    return True


def _chunked_bulk_create(objects, chunk_size=1000):
    """
    Bulk creates a list of objects in chunks.

    Args:
        objects (list): The list of objects to be created.
        chunk_size (int, optional): The size of each chunk. Defaults to 1000.

    Returns:
        None
    """
    for i in range(0, len(objects), chunk_size):
        Data.objects.bulk_create(objects[i:i + chunk_size])


def save_nhanes_data(df, cycle_id, dataset_id):
    """
    Saves NHANES data to the database.

    Args:
        df (pandas.DataFrame): The NHANES data as a pandas DataFrame.
        cycle_id (int): The ID of the cycle to associate the data with.
        dataset_id (int): The ID of the dataset to associate the data with.

    Returns:
        bool: True if the data was successfully saved, False otherwise.
    """
    try:
        cycle = Cycle.objects.get(id=cycle_id)
        dataset = Dataset.objects.get(id=dataset_id)
    except (Cycle.DoesNotExist, Dataset.DoesNotExist):
        print("Cycle or Dataset not found.")
        return False

    # Check if data already exists for this cycle and dataset
    if Data.objects.filter(cycle=cycle, dataset=dataset).exists():
        print(
            "Data already exists for this cycle and dataset. No updates will \
            be performed."
            )
        return False

    # Load only the fields that are present in the database
    field_names = df.columns.tolist()

    fields = {
        field.field: field for field in Field.objects.filter(
            field__in=field_names
            ).only(
                'id', 'field'
                )
        }

    # Check if all fields are present in the database
    missing_fields = [name for name in field_names if name not in fields]
    if missing_fields:
        print(f"Missing fields: {missing_fields}")
        return False

    # Prepare the data to be inserted
    to_create = [
        Data(
            cycle=cycle,
            dataset=dataset,
            field=fields[col_name],
            sample=index,
            value=str(value)
        )
        for col_name in df.columns if col_name in fields
        for index, value in df[col_name].items()
    ]

    # Using a transaction to avoid partial inserts
    # Using bulk_create to speed up the process
    with transaction.atomic():
        _chunked_bulk_create(to_create)

    print(
        f"All data for cycle {cycle_id} and dataset {dataset_id} \
        has been inserted."
        )
    return True


def _download_file(url, path):
    """
    Downloads a file from the given URL and saves it to the specified path.

    Args:
        url (str): The URL of the file to download.
        path (str): The path where the downloaded file should be saved.

    Returns:
        tuple: A tuple containing a boolean value indicating whether the
        download was successful and an error message (if any).

    Raises:
        Exception: If an error occurs during the download process.

    """
    error = ''
    try:
        # Check if the URL is a HTML page
        if url.endswith('.htm') or url.endswith('.html'):
            is_html_page = True
        else:
            is_html_page = False

        response = requests.get(url, stream=True, allow_redirects=True)

        # When file does not exist it redirects to a page that returns 200
        # as a solution to this, we check if the content-type is html
        content_type = response.headers.get('Content-Type')

        # Apply the 'text/html' check only if it's not a known .htm/.html URL
        if not is_html_page and 'text' in content_type and 'html' in content_type:  # noqa E501
            print(f"Failed to download {url}. The URL returned a HTML page, likely an error page.")  # noqa E501
            error = 'no_file'
            return False, error

        if response.status_code == 200:
            with open(path, 'wb') as f:
                content_length = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    content_length += len(chunk)

                # Check if the downloaded file is too small
                if content_length < 1024:
                    print(f"Downloaded file from {url} seems too small. Check if it's the expected file.")  # noqa E501
                    error = 'no_file'
                    return False, error

            print(f"Downloaded {url}")
            return True, error
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}") # noqa E501
            error = 'error'
            return False, error
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        error = 'error'
        return False, error


def download_nhanes_files():
    """
    Downloads NHANES files from the specified URLs and processes the
    downloaded data.

    Returns:
        bool: True if the download and processing are successful, False
        otherwise.
    """
    qs_load_metadata = SystemConfig.objects.filter(
        config_key='load_metadata'
    ).first()

    # Filter datasets with status pending and is_download True
    qry_datasets = DatasetControl.objects.filter(
        status='pending',
        is_download=True
    )

    # loop all datasets market to load
    for qs_dataset in qry_datasets:
        # set files names
        dataset = qs_dataset.dataset.dataset
        if qs_dataset.cycle.year_code is not None:
            name_file = f"{dataset}_{qs_dataset.cycle.year_code}"
        else:
            name_file = f"{dataset}"

        if qs_dataset.has_special_year_code:
            if qs_dataset.special_year_code is not None:
                name_file = f"{dataset}_{qs_dataset.special_year_code}"
            else:
                name_file = f"{dataset}"

        # setting folder to hosting download files
        base_dir = Path(settings.BASE_DIR) / str(qs_dataset.cycle.base_dir)
        os.makedirs(base_dir, exist_ok=True)

        data_file = base_dir / f"{name_file}.XPT"
        doc_file = base_dir / f"{name_file}.htm"

        # set URLs
        data_url = qs_dataset.cycle.get_dataset_url(f"{name_file}.XPT")
        doc_url = data_url.replace('XPT', 'htm')

        # download XPT data
        sleep(np.random.rand())  # Avoid being blocked
        if qs_dataset.status != 'data_downloaded':
            if not os.path.exists(data_file):
                status, error = _download_file(data_url, data_file)
                if status:
                    qs_dataset.status = 'data_downloaded'
                else:
                    qs_dataset.status = error
                    qs_dataset.save()
                    continue
            else:
                qs_dataset.status = 'data_downloaded'
                print(f"File {data_file} already exists. Skipping download.")

        # download doc data
        sleep(np.random.rand())  # Avoid being blocked
        if qs_dataset.status != 'doc_downloaded':
            if not os.path.exists(doc_file):
                if _download_file(doc_url, doc_file):
                    qs_dataset.status = 'doc_downloaded'
                else:
                    qs_dataset.status = 'error'
                    qs_dataset.save()
                    continue
            else:
                qs_dataset.status = 'doc_downloaded'
                print(f"File {doc_file} already exists. Skipping download.")

        # if error, save and continue
        if qs_dataset.status == 'error':
            qs_dataset.save()
            continue

        # Get data from XPT file
        try:
            df, meta_df = _get_data_from_xpt(data_file)
        except Exception as e:
            try:
                os.remove(data_file)
                os.remove(doc_file)
            except OSError as e:
                print(f"Error deleting file: {e}")
            print(f"Error reading XPT file: {e}")
            qs_dataset.status = 'error'
            qs_dataset.save()
            continue

        # Get data from HTM file
        variable_df, code_table = _get_data_from_htm(dataset, doc_file)
        if variable_df is None or code_table is None:
            print(f"Error reading HTM file: {doc_file}")
            qs_dataset.status = 'error'
            qs_dataset.save()
            continue

        # Normalization of the variable names
        df_metadata = pd.merge(
            variable_df,
            meta_df[['Variable', 'Type']],
            left_on='VariableName',
            right_on='Variable',
            how='left'
        )

        # Converter code_table to JSON
        json_tables = {key: value.to_json(orient='records') for key, value in code_table.items()}  # noqa E501

        # Create a column in 'combined_df' for the code table
        df_metadata['CodeTables'] = df_metadata['VariableName'].map(json_tables)  # noqa E501

        # Salve the metadata in the database
        process_and_save_metadata(
            df_metadata,
            dataset_id=qs_dataset.dataset.id,
            cycle_id=qs_dataset.cycle.id,
            load_metadata=qs_load_metadata.config_value
            )

        # Write Fields and FieldCycle tables
        check_data = save_nhanes_data(
            df,
            cycle_id=qs_dataset.cycle.id,
            dataset_id=qs_dataset.dataset.id,
            )

        # Clean up downloaded files
        try:
            os.remove(data_file)
            os.remove(doc_file)
        except OSError as e:
            print(f"Error deleting file: {e}")

        # Update the DatasetCycle table
        if check_data:
            # TODO: Add Description
            # qs_dataset.dataset.description = ''
            qs_dataset.metadata_url = doc_url
            qs_dataset.status = 'complete'
            # TODO: Extract JSON from HTML (_parse_nhanes_html_docfile)
            # metadata.description = "JSON"
            qs_dataset.save()

        print("Termino do processamento do dataset: ", dataset)

    return True

# End of the file
# File: nhanes/services/loader.py
