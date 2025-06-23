import pandas as pd  # noqa
from django.http import HttpResponse
from django.contrib import messages


def download_results_as_csv(
        request,
        df,
        file_name="MyNHANES_Report"
        ):
    """
    Creates an HTTP response to download the DataFrame as a CSV file.
    """
    try:
        # Create an HTTP response with a download header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

        df.to_csv(
            path_or_buf=response,
            sep=',',
            index=False,
            encoding='utf-8'
        )

        messages.success(request, "CSV download completed successfully.")
        return response

    except Exception as e:
        # Send an error message to the admin
        messages.error(request, f"Error generating CSV: {str(e)}")
        return None
