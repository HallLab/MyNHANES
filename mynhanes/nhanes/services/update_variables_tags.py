import pandas as pd
from nhanes.models import Variable, Tag
from django.core.exceptions import ObjectDoesNotExist


def update_variables_tags_from_csv(file_path):
    # read the CSV file
    df = pd.read_csv(file_path)

    # list all tags
    all_tags = Tag.objects.all()

    # interate over the rows of the CSV file
    for index, row in df.iterrows():
        variable_name = row["Variable"]

        try:
            # try to get the variable by name
            variable = Variable.objects.get(variable=variable_name)

            # remove all tags from the variable
            variable.tags.clear()

            # interate over all tags
            for tag in all_tags:
                if row.get(tag.tag, "").lower() == "x":
                    variable.tags.add(tag)

            print(f"Updated: {variable_name}")

        except ObjectDoesNotExist:
            print(f"Variable not found: {variable_name}")

    print("Done")
