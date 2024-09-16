import pandas as pd
from django.contrib import messages
from nhanes.models import VariableCycle
from django.shortcuts import redirect
from .utils import download_results_as_csv


def _queryset_to_dataframe(variable_cycles):
    # Prepare data for the DataFrame
    data = []
    for var_cycle in variable_cycles:
        data.append({
            "Version": var_cycle.version.version,
            "Variable": var_cycle.variable.variable,
            "Dataset": var_cycle.dataset.dataset,
            "Cycle": var_cycle.cycle.cycle,
            "Variable Name": var_cycle.variable_name,
            "SAS Label": var_cycle.sas_label,
            "English Text": var_cycle.english_text,
            "Target": var_cycle.target,
            "Type": var_cycle.type,
            "Value Table": str(var_cycle.value_table)
        })

    # Convert the data into a DataFrame
    return pd.DataFrame(data)


def report_selected_variable_cycles(modeladmin, request, queryset=None):

    try:
        variable_cycles = queryset

        df = _queryset_to_dataframe(variable_cycles)

        response = download_results_as_csv(
            request,
            df,
            file_name="Report_Variable_Cycles"
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


def report_all_variable_cycles(modeladmin, request, queryset=None):

    try:
        variable_cycles = VariableCycle.objects.all()

        df = _queryset_to_dataframe(variable_cycles)

        response = download_results_as_csv(
            request,
            df,
            file_name="Report_Variable_Cycles"
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
