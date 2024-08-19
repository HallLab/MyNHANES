
import importlib
import pandas as pd
from nhanes.models import NormalizationRule, RawData
# from nhanes.workprocess.normalization_base import BaseNormalization


class NormalizationManager:

    def __init__(self):
        self.rules = NormalizationRule.objects.filter(is_active=True)

    def apply_all_transformations(self):
        for rule in self.rules:
            # import the normalization dynamically based on the rule name
            module_name = f"nhanes.normalizations.{rule.rule}.{rule.file_name.split('.')[0]}"  # noqa E501
            transformation_module = importlib.import_module(module_name)
            # class needs to be the same name as the file
            class_name = rule.file_name.split('.')[0]
            transformation_class = getattr(transformation_module, class_name)

            # get destination fields and types from NormalizationRule Model
            destination_fields = {
                field.field: field.field_type for field in rule.destination_fields.all()
                }

            # load the input data from RawData
            input_df = self._get_input_data(rule)

            # instantiate the normalization class
            normalization_instance = transformation_class(
                input_df=input_df,
                destination_fields=destination_fields,
                )

            # apply the normalization
            result_df = normalization_instance.apply_normalization()

            if result_df is None:
                continue

            # check if the field types are correct
            check = normalization_instance.field_type()
            if not check:
                ...

            # save the output data in NormalizedData
            # self._save_output_data(normalization_instance, rule)
            check = normalization_instance.save_output_data()
            if not check:
                ...

    # get the input data from RawData
    def _get_input_data(self, rule):
        """
        Read the input data from RawData based on the source variables of the rule.
        """
        variable_ids = rule.source_variables.values_list('id', flat=True)
        qs_df = RawData.objects.filter(variable_id__in=variable_ids).values(
            'cycle',
            'dataset',
            'sample',
            'sequence',
            'variable',
            'variable_id__variable',
            'value',
            )
        data = list(qs_df)
        df = pd.DataFrame(data)

        # Pivot the DataFrame
        pivot_df = df.pivot_table(
                index=['cycle', 'dataset', 'sample', 'sequence'],
                columns='variable_id__variable',
                values='value',
                aggfunc='first'
            )
        pivot_df = pivot_df.reset_index()
        pivot_df.columns.name = None
        return pivot_df
