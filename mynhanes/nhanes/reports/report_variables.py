import pandas as pd
from nhanes.models import Variable, Tag
from django.contrib import messages
from django.shortcuts import redirect
from .utils import download_results_as_csv


def _queryset_to_dataframe(all_tags, variables):
    data = []
    for variable in variables:
        # Create a dictionary for each variable
        var_data = {
            "Variable": variable.variable,
            "Description": variable.description,
            "Is Active": variable.is_active,
            "Type": variable.type
        }

        # Check if the variable has each tag and mark it with 'x' if present
        for tag in all_tags:
            var_data[tag] = "x" if variable.tags.filter(tag=tag).exists() else ""

        data.append(var_data)

    return pd.DataFrame(data)


def report_selected_variables(modeladmin, request, queryset):

    try:
        all_tags = Tag.objects.all().values_list('tag', flat=True)
        variables = queryset.prefetch_related('tags')

        df = _queryset_to_dataframe(all_tags, variables)

        response = download_results_as_csv(
            request,
            df,
            file_name="Report_Variables_Tags"
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


def report_all_variables(modeladmin, request, queryset):

    try:
        all_tags = Tag.objects.all().values_list('tag', flat=True)
        variables = Variable.objects.all().prefetch_related('tags')

        df = _queryset_to_dataframe(all_tags, variables)

        response = download_results_as_csv(
            request,
            df,
            file_name="Report_Variables_Tags"
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
