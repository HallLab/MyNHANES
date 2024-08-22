import requests
from io import StringIO
import string
import pandas as pd
import pyreadstat
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from nhanes.models import (
    Version,
    Variable,
    VariableCycle,
    Dataset,
    Cycle,
    DatasetCycle,
    Data
    )
from nhanes.utils.logs import logger


class EmptySectionError(Exception):
    pass


def _read_xpt_with_multiple_encodings(log, file_path):
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'utf-16']
    for encoding in encodings:
        try:
            df, meta = pyreadstat.read_xport(file_path, encoding=encoding)
            msm = f"File read successfully with encoding: {encoding}"
            logger(log, "i", msm)
            return df, meta
        except UnicodeDecodeError as e:
            msm = f"UnicodeDecodeError with encoding {encoding}: {e}"
            logger(log, "w", msm)
        except Exception as e:
            msm = f"Error reading XPT file with encoding {encoding}: {e}"
            logger(log, "e", msm)
    # if all encodings failed, return None and an error message
    msm = "Failed to read XPT file with all attempted encodings"
    logger(log, "e", msm)
    # return None, msm
    raise ValueError("Failed to read XPT file with all attempted encodings")


def get_data_from_xpt(log, datafile):
    """
    Attempts to read the XPT file and extract the data and metadata.
    If the reading fails, logs the error and returns None.
    Args:
        log (logger): Logger object to log messages.
        datafile (str): Path to the XPT data file.

    Returns:
        tuple: A tuple containing the DataFrame of the data and a
                DataFrame of the metadata.
    """
    try:
        # df, meta = pyreadstat.read_xport(datafile)
        df, meta = _read_xpt_with_multiple_encodings(log, datafile)
    except Exception as e:
        msm = f"Error reading XPT file: {e}"
        logger(log, "e", msm)
        raise ValueError(f"Error reading XPT file: {e}")
    if df is None:
        logger(log, "e", {meta})
        raise ValueError(f"Error reading XPT file: {meta}")

    # ensure SEQN is treated as an integer
    df['SEQN'] = df['SEQN'].astype(int)

    # reset index if 'SEQN' was initially set as index
    if 'SEQN' in df.index.names:
        df = df.reset_index()

    # add a sequence number for each SEQN
    df['sequence'] = df.groupby('SEQN').cumcount()
    # list to store metadata of all variables
    all_metadata = []

    # iterate over all variables
    for var_name in meta.column_names:
        # get specific metadata for each variable
        variable_labels = meta.column_names_to_labels.get(var_name, "")
        variable_measurements = meta.readstat_variable_types.get(
            var_name,
            None
            )
        # create a dictionary with relevant metadata
        metadata_dict = {
            'Variable': var_name,
            'Type': variable_measurements,
            'Labels': variable_labels,
        }
        all_metadata.append(metadata_dict)

    # convert the list of dictionaries into a DataFrame
    df_metadata = pd.DataFrame(all_metadata)

    return df, df_metadata


def _parse_html_variable_info_section(info):
    """
    """
    infodict = {
        i[0].text.strip(': ').replace(' ', ''): i[1].text.strip()
        for i in zip(info.find_all('dt'), info.find_all('dd'))
    }
    infodict['VariableNameLong'] = ''.join([i.title() for i in infodict['SASLabel'].translate(str.maketrans('', '', string.punctuation)).split(' ')]) if 'SASLabel' in infodict else infodict['VariableName'] # noqa E501

    return infodict


def _parse_html_variable_section(
        source_code,
        section,
        variable_df,
        code_table,
        ):
    """
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
        msm = f"Error parsing HTML documentation file: {e}"
        print(msm)  # replace to logger
        return variable_df, code_table


def get_data_from_htm(doc_code, docfile):
    """
    """
    variable_dfs = {}
    code_table = {}
    variable_df = None

    variable_dfs[doc_code], code_tables = _parse_nhanes_html_docfile(
        doc_code,
        docfile
    )

    if not code_tables:
        return variable_df, code_table

    code_table.update(code_tables)

    for code in variable_dfs:
        if variable_df is None:
            variable_df = variable_dfs[code]
        else:
            variable_df = pd.concat((variable_df, variable_dfs[code]))
    return variable_df, code_table


def process_and_save_metadata(
        log,
        df,
        dataset_id,
        cycle_id,
        load_metadata=True,
        dataset_cycle_url="",
        dataset_cycle_description="",
        ):
    """
    """

    try:
        qry_dataset = Dataset.objects.get(id=dataset_id)
        qry_cycle = Cycle.objects.get(id=cycle_id)
        qry_version = Version.objects.get(version='nhanes')
    except ObjectDoesNotExist as e:
        msm = f"Dataset or Cycle not found on process_and_save_metadata function: {e}"
        logger(log, "e", msm)
        return False

    # Uptade all or nothing and return False if any error occurs
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                variable, created = Variable.objects.get_or_create(
                    variable=row['VariableName'],
                    defaults={
                        'description': row['SASLabel'],
                        'type': 'oth',
                    }
                )
                
                if load_metadata:
                    DatasetCycle.objects.filter(
                        dataset=qry_dataset,
                        cycle=qry_cycle
                    ).update(
                            metadata_url=dataset_cycle_url,
                            description=dataset_cycle_description
                    )
                    variable_m, create_m = VariableCycle.objects.update_or_create(
                        variable=variable,
                        cycle=qry_cycle,
                        defaults={
                            'version': qry_version,
                            'variable_name': row['VariableName'],
                            'sas_label': row['SASLabel'],
                            'english_text': row['EnglishText'],
                            'target': row['Target'],
                            'type': row['Type'],
                            'value_table': row['CodeTables']
                        }
                    )
                else:
                    variable_m, create_m = VariableCycle.objects.update_or_create(
                        variable=variable,
                        cycle=qry_cycle,
                        defaults={
                            'version': qry_version,
                            'variable_name': row['VariableName'],
                            'sas_label': row['SASLabel'],
                            'english_text': '',
                            'target': '',
                            'type': row['Type'],
                            'value_table': ''
                        }
                    )
                msm = f"Processed {variable.variable} with status {'created' if created else 'updated'}." # noqa E501
                logger(log, "i", msm)
            except IntegrityError as e:
                msm = f"Database error while processing {row['VariableName']}: {e}"
                logger(log, "e", msm)
                return False
            except Exception as e:
                msm = f"An unexpected error occurred: {e}"
                logger(log, "e", msm)
                return False
    return True


def _chunked_bulk_create(objects, chunk_size=1000):
    """
    """
    for i in range(0, len(objects), chunk_size):
        Data.objects.bulk_create(objects[i:i + chunk_size])


def save_nhanes_data(log, df, cycle_id, dataset_id):
    """
    """
    try:
        cycle = Cycle.objects.get(id=cycle_id)
        dataset = Dataset.objects.get(id=dataset_id)
        version = Version.objects.get(version='nhanes')
    except (Cycle.DoesNotExist, Dataset.DoesNotExist):
        msm = "Dataset or Cycle not found on save_nhanes_data function."
        logger(log, "e", msm)
        return False

    # check if data already exists for this cycle and dataset for any version
    if Data.objects.filter(cycle=cycle, dataset=dataset).exists():
        msm = "Data already exists for this cycle and dataset. No updates will \
            be performed."
        logger(log, "w", msm)
        return False

    # load only the fields that are present in the database
    Variable_names = df.columns.tolist()

    variable = {
        variable.variable: variable for variable in Variable.objects.filter(
            variable__in=Variable_names
            ).only(
                'id', 'variable'
                )
        }

    # check if all fields are present in the database
    # missing_fields = [name for name in Variable_names if name not in fields]
    missing_fields = [name for name in Variable_names if name not in variable and name != 'sequence']  # noqa E501
    if missing_fields:
        msm = f"Missing fields: {missing_fields}"
        logger(log, "e", msm)
        return False

    # pre-processing the data to extract SEQN and sequence for faster access
    seqn_values = df['SEQN']
    sequence_values = df['sequence']

    # list comprehension
    to_create = [
        Data(
            version=version,
            cycle=cycle,
            dataset=dataset,
            variable=variable[col_name],
            sample=seqn_values[index],
            sequence=sequence_values[index],
            value=str(value)
        )
        for col_name in (set(df.columns) - {'SEQN', 'sequence'})
        if col_name in variable
        for index, value in df[col_name].items()
    ]

    # using a transaction to avoid partial inserts
    # using bulk_create to speed up the process
    with transaction.atomic():
        _chunked_bulk_create(to_create)

    msm = f"All data for cycle {cycle_id} and dataset {dataset_id} \
        has been inserted."
    logger(log, "i", msm)
    return True


def download_nhanes_file(log, url, path):
    """
    """
    error = ''
    try:
        # check if the URL is a HTML page
        if url.endswith('.htm') or url.endswith('.html'):
            is_html_page = True
        else:
            is_html_page = False

        response = requests.get(url, stream=True, allow_redirects=True)

        # when file does not exist it redirects to a page that returns 200
        # as a solution to this, we check if the content-type is html
        content_type = response.headers.get('Content-Type')

        # apply the 'text/html' check only if it's not a known .htm/.html URL
        if not is_html_page and 'text' in content_type and 'html' in content_type:  # noqa E501
            msm = f"Failed to download {url}. The URL returned a HTML page, likely an error page."  # noqa E501
            logger(log, "e", msm)
            error = 'no_file'
            return False, error

        if response.status_code == 200:
            with open(path, 'wb') as f:
                content_length = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    content_length += len(chunk)

                # check if the downloaded file is too small
                if content_length < 1024:
                    msm = f"Downloaded file from {url} seems too small. Check if it's the expected file." # noqa E501
                    logger(log, "w", msm)
                    error = 'no_file'
                    return False, error

            msm = f"Downloaded {url}"
            logger(log, "s", msm)
            return True, error
        else:
            msm = f"Failed to download {url}. Status code: {response.status_code}" # noqa E501
            logger(log, "e", msm)
            error = 'error'
            return False, error
    except Exception as e:
        msm = f"Error downloading {url}: {str(e)}"
        logger(log, "e", msm)
        error = 'error'
        return False, error
