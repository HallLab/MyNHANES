import pandas as pd
from django.contrib import messages
from nhanes.models import DatasetCycle
from django.shortcuts import redirect
from .utils import download_results_as_csv


def _queryset_to_dataframe(dataset_cycles):
    # Prepare data for the DataFrame
    data = []
    for ds_cycle in dataset_cycles:
        data.append({
            "Dataset": ds_cycle.dataset.dataset,
            "Cycle": ds_cycle.cycle.cycle,
            "Metadata URL": ds_cycle.metadata_url,
            "Description": ds_cycle.description,
            "Observation": ds_cycle.observation,
            "Has Special Year Code": "Yes" if ds_cycle.has_special_year_code else "No",
            "Special Year Code": ds_cycle.special_year_code,
            "Has Dataset": "Yes" if ds_cycle.has_dataset else "No"
        })

    # Convert the data into a DataFrame
    return pd.DataFrame(data)


def report_selected_dataset_cycles(modeladmin, request, queryset=None):

    try:
        dataset_cycles = queryset

        df = _queryset_to_dataframe(dataset_cycles)

        response = download_results_as_csv(
            request,
            df,
            file_name="Report_Dataset_Cycles"
            )

        if response is None:
            return None

        return response

    except Exception as e:
        modeladmin.message_user(
            request,
            f"Error generating report: {str(e)}",
            level=messages.ERROR
            )
        # return None
        return redirect(request.path)


def report_all_dataset_cycles(modeladmin, request, queryset=None):

    try:
        dataset_cycles = DatasetCycle.objects.all()

        df = _queryset_to_dataframe(dataset_cycles)

        response = download_results_as_csv(
            request,
            df,
            file_name="Report_Dataset_Cycles"
            )

        if response is None:
            return None

        return response

    except Exception as e:
        modeladmin.message_user(
            request,
            f"Error generating report: {str(e)}",
            level=messages.ERROR
            )
        # return None
        return redirect(request.path)
