import os
from django.db.models import Q, F
from nhanes.models import Data, QueryColumns, VariableCycle, DatasetCycle
import pandas as pd
from django.http import HttpResponse
import dask.dataframe as dd
from dask.distributed import Client


def _create_pivot_table(
        df,
        index_columns,
        pivot_columns,
        value_column='value',
        no_conflict=False,
        no_multi_index=False
        ):
    """
    Creates a dynamic pivot table based on the specified columns.

    This function takes a DataFrame and a set of columns to use as the index,
    pivot columns, and a value column. It then creates a pivot table from the
    DataFrame using these columns.

    Parameters
    ----------
    df : pandas.DataFrame
        The original DataFrame.
    index_columns : list of str
        The list of columns to use as the index.
    pivot_columns : list of str
        The list of columns to use as pivot columns.
    value_column : str
        The name of the column whose values will be distributed across the
        pivot.

    Returns
    -------
    pandas.DataFrame
        The pivoted DataFrame.
    """

    # Check if all required columns are present in the DataFrame
    missing_cols = set(index_columns + pivot_columns + [value_column]) - set(df.columns)  # noqa: E501
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Create a unique index to avoid conflicts in the pivot table
    df['unique_index'] = df['Cycle'].astype(str) + \
        '___' + df['sample'].astype(str) + \
        '___' + df['sequence'].astype(str)
    df['unique_index'] = df['unique_index'].astype('category')

    if len(pivot_columns) > 1:
        # Create a unique column to avoid conflicts in the pivot table
        df['unique_column'] = df[pivot_columns].apply(
            lambda row: '___'.join(row.values.astype(str)),
            axis=1
            )
        df['unique_column'] = df['unique_column'].astype('category')
    else:
        df['unique_column'] = df[pivot_columns].astype('category')

    df.drop(columns=index_columns, inplace=True)
    df.drop(columns=pivot_columns, inplace=True)

    if no_conflict:
        # TODO: Repensar sobre esse ponto
        # # Use a lambda function to check for conflicts in the values
        # # If there are conflicts, set the value to 'Conflict'
        # pivot_df = df.pivot_table(
        #     index=index_columns,
        #     columns=pivot_columns,
        #     values=value_column,
        #     # TODO: Check if this is the best way to handle conflicts
        #     aggfunc=lambda x: 'Conflict' if len(x) > 1 else x.iloc[0]
        # )
        ...
    else:
        # Configura um cliente Dask com um número específico de trabalhadores
        # e memória limitada
        client = Client(n_workers=6, threads_per_worker=1, memory_limit='5GB')
        print(client.dashboard_link)
        # Imprime o link do dashboard para monitoramento

        partition_size = df.memory_usage(deep=True).sum() / len(df)
        print(f"Partition size: {partition_size:.2f} bytes")

        # desired_partition_size = 100e6  # 100 MB por partição
        desired_partition_size = 20e6  # 50 MB per partitio
        n_partitions = int(
            df.memory_usage(deep=True).sum() / desired_partition_size
            )
        if n_partitions < 1:
            n_partitions = 1

        dask_df = dd.from_pandas(df, npartitions=n_partitions)
        # dask_df = dd.from_pandas(df, npartitions=10)

        pivot_dd = dask_df.pivot_table(
            index='unique_index',
            columns='unique_column',
            values='value',
            aggfunc='first'
        )

        pivot_df = pivot_dd.compute()

        if len(pivot_columns) > 1:
            # Transform single columns to multi-index columns
            new_columns = [col.split('___') for col in pivot_df.columns]
            multiindex_columns = pd.MultiIndex.from_tuples(new_columns)
            pivot_df.columns = multiindex_columns
        else:
            ...

        # Reset index and split unique_index to original columns
        pivot_df[
            ['Cycle', 'sample', 'sequence']
            ] = pivot_df.index.to_series().str.split('___', expand=True)

        pivot_df.reset_index(inplace=True)
        pivot_df.drop(columns=['unique_index',], inplace=True)
        pivot_df.set_index(['Cycle', 'sample', 'sequence'], inplace=True)

    return pivot_df


def _download_query_results_as_csv(
        request,
        pivot_df,
        file_name="Nhanes_Report"
        ):
    """
    Download the results of a query as a CSV file.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request.
    pivot_df : pandas.DataFrame
        The DataFrame containing the query results.
    file_name : str, optional
        The name of the file to download. Default is 'Nhanes_Report'.

    Returns
    -------
    django.http.HttpResponse
        The HTTP response containing the CSV file.
    """
    # Create an HTTP response with a download header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

    # Write the DataFrame to the CSV file directly in the response
    pivot_df.to_csv(
        path_or_buf=response,
        sep=',',
        index=True,
        encoding='utf-8'
        )

    return response


def _parse_filter_value(operator, value):
    if operator == 'in':
        # Assume que os valores são separados por vírgula
        return [v.strip() for v in value.split(',')]
    elif operator == 'range':
        # Assume que os valores são separados por hífen e são números
        return [int(v) for v in value.split('-')]
    elif operator == 'isnull':
        # Corretamente converte string para booleano
        return value.lower() in ('true', '1', 't')
    # Os outros operadores que você listou realmente não necessitam conversão
    # para inteiros e devem trabalhar diretamente com strings
    return value


def _parse_file_filter(file_path, filter_field):
    """
    Parses a file to extract values from the first column and prepares a Q
    object for filtering.

    Args:
        file_path (str): Path to the file containing filter values.
        filter_field (str): Name of the field on which to apply the filter.

    Returns:
        dict: Dictionary with filter conditions.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, 'r') as file:
        values = [line.strip().split(',')[0] for line in file if line.strip()]

    # Make sure there are values to filter on to avoid empty 'in' queries
    if not values:
        raise ValueError("No values found in the file to apply filter.")

    return {f'{filter_field}__in': values}


def download_data_report(modeladmin, request, queryset):
    """
    Download the results of a query from the admin interface.

    Parameters
    ----------
    modeladmin : django.contrib.admin.ModelAdmin
        The admin model.
    request : django.http.HttpRequest
        The HTTP request.
    queryset : django.db.models.query.QuerySet
        The queryset containing the selected objects.

    Returns
    -------
    django.http.HttpResponse or None
        The HTTP response containing the CSV file, or None if there was an
        error.
    """
    if queryset.count() > 1:
        modeladmin.message_user(
            request,
            "Please select only one query structure at a time.",
            level='error'
            )
        return

    # TODO check why the filters is not being used on select at line 272
    query_structure = queryset.first()
    qs_filters = query_structure.filters.all()
    qs_report_columns = query_structure.columns.all()

    if not qs_filters:
        modeladmin.message_user(
            request,
            "No filters found in the query structure. ",
            level='error'
            )
        return

    # Get all data in lazy mode
    data_query = Data.objects.all()

    query = Q()
    for filter_obj in qs_filters:
        # Parse the filter value based on the operator
        value = _parse_filter_value(filter_obj.operator, filter_obj.value)
        # if operator == '_eq' no use in the variable (default is eq)
        if filter_obj.operator == 'file':
            kwargs = _parse_file_filter(
                filter_obj.value,
                filter_obj.filter_name
                )

        elif filter_obj.operator == 'eq':
            kwargs = {f'{filter_obj.filter_name}': value}
        else:
            kwargs = {f'{filter_obj.filter_name}__{filter_obj.operator}': value}  # noqa: E501

        query &= Q(**kwargs)  # Using AND to combine filters

    data_query = data_query.filter(query)

    # Standard columns
    column_names = ['cycle__cycle', 'sample', 'sequence', 'value']
    # Personalized columns
    new_columns = [col.internal_data_key for col in qs_report_columns]
    # Remove duplicates
    new_columns = [col for col in new_columns if col not in column_names]
    column_names.extend(new_columns)

    data_query = data_query.values_list(*column_names)

    if not data_query:
        modeladmin.message_user(
            request,
            "No data found in the query structure. ",
            level='error'
            )
        return

    df = pd.DataFrame(list(data_query), columns=column_names)

    # SELECT internal_data_key, column_name
    column_mappings = QueryColumns.objects.filter(
        internal_data_key__in=column_names
        ).values('internal_data_key', 'column_name')

    # Create a dictionary to map internal_data_key to column_name
    rename_dict = {
        mapping['internal_data_key']: mapping['column_name'] for mapping in column_mappings  # noqa: E501
        }
    df.rename(columns=rename_dict, inplace=True)

    # Define index and pivot columns
    index_cols = ['Cycle', 'sample', 'sequence']  # [0.2.0]
    pivot_cols = [col.column_name for col in qs_report_columns]
    pivot_cols = [col for col in pivot_cols if col not in index_cols]

    # Create the pivot table
    pivot_df = _create_pivot_table(
        df,
        index_columns=index_cols,
        pivot_columns=pivot_cols,
        no_conflict=query_structure.no_conflict,
        no_multi_index=query_structure.no_multi_index
        )

    # Download the results as a CSV file
    return _download_query_results_as_csv(
        request,
        pivot_df,
        query_structure.structure_name
        )


# 0.2.0: Master Data Report
def fields_report(output_path):
    """
    Generate a master data report and save it to the specified output path.

    Args:
        output_path (str): The path where the report will be saved.

    Returns:
        bool: True if the report is successfully saved, False otherwise.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        print("the directory does not exist")
        return False
        # os.makedirs(output_dir)

    # Get the basic fields and details
    basic_fields_qs = Data.objects.values(
        cycle_name=F('cycle__cycle'),
        group=F('dataset__group__group'),
        dataset_dataset=F('dataset__dataset'),
        dataset_description=F('dataset__description'),
        variable_variable=F('variable__variable'),
        variable_description=F('variable__description')
    ).distinct()
    basic_df = pd.DataFrame(list(basic_fields_qs))

    # Get the field cycle details
    cycle_details_qs = VariableCycle.objects.values(
        variable_variable=F('variable__variable'),
        cycle_cycle=F('cycle__cycle'),
        Field_Text=F('english_text'),
        Field_Target=F('target'),
        Data_Type=F('type'),
        Data_Table=F('value_table')
    ).distinct()
    details_df = pd.DataFrame(list(cycle_details_qs))

    final_df = pd.merge(
        basic_df,
        details_df,
        on=['field_name',
            'cycle_name'
            ],
        how='left'
        )

    final_df.to_csv(output_path, index=False)
    print(f"Report saved to {output_path}")

    return True


# 0.2.0: Dataset Status Report
def control_report(output_path):
    """
    Generate a control report and save it to the specified output path.

    Args:
        output_path (str): The path where the control report will be saved.

    Returns:
        bool: True if the control report is successfully saved.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        print("the directory does not exist")
        return False
        # os.makedirs(output_dir)

    # Get the basic fields and details
    basic_qs = DatasetCycle.objects.values(
        Cycle_Name=F('cycle__cycle'),
        Group=F('dataset__group__group'),
        Dataset_Name=F('dataset__dataset'),
        Dataset_Description=F('dataset__description'),
        Nhanes_Link=F('metadata_url'),
        Special_Code=F('has_special_year_code'),
        Special_Code_Value=F('special_year_code'),
        Will_Load=F('is_download'),
        Status_Load=F('status')
    ).distinct()
    basic_df = pd.DataFrame(list(basic_qs))
    basic_df.to_csv(output_path, index=False)
    print(f"Report saved to {output_path}")

    return True
