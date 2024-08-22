
import importlib
import pandas as pd
from nhanes.models import Rule, RuleVariable, Data


class NormalizationManager:

    def __init__(self):
        self.rules = Rule.objects.filter(is_active=True)

    def apply_all_transformations(self):
        for rule in self.rules:
            # import the normalization dynamically based on the rule name
            module_name = f"nhanes.normalizations.{rule.rule}.{rule.file_script.split('.')[0]}"  # noqa E501
            transformation_module = importlib.import_module(module_name)
            # class needs to be the same name as the file
            class_name = rule.file_script.split('.')[0]
            transformation_class = getattr(transformation_module, class_name)

            # QuerySets para as variáveis de destino e origem
            qs_target_variable = RuleVariable.objects.filter(rule=rule, is_source=False)
            qs_source_variable = RuleVariable.objects.filter(rule=rule, is_source=True)

            # load the input data from RawData
            input_df = self._get_input_data(qs_source_variable)

            # instantiate the normalization class
            normalization_instance = transformation_class(
                input_df=input_df,
                target_variable=qs_target_variable,
                )

            # apply the normalization
            check = normalization_instance.apply_normalization()

            # self.validate_output_variables()

            # df_output = self.filter_output_columns()

            # if result_df is None:
            #     continue

            # check if the field types are correct
            check = normalization_instance.field_type()
            if not check:
                ...

            # save the output data in NormalizedData
            check = normalization_instance.save_output_data(rule)
            if not check:
                ...

    # get the input data from RawData
    def _get_input_data(self, qs_source_variable):
        """
        Read the input data from RawData based on the source variables of the rule.
        """

        # Filtrando os dados no modelo Data com base nos pares (dataset, variable)
        qs_df = Data.objects.filter(
            dataset_id__in=qs_source_variable.values_list('dataset_id', flat=True),
            variable_id__in=qs_source_variable.values_list('variable_id', flat=True)
        ).values(
            'version',
            'cycle',
            'dataset',
            'sample',
            'sequence',
            'variable',
            'variable_id__variable',
            'value',
        )

        # Convertendo para DataFrame
        data = list(qs_df)
        df = pd.DataFrame(data)

        # Pivot the DataFrame
        pivot_df = df.pivot_table(
                index=['version', 'cycle', 'dataset', 'sample', 'sequence'],
                columns='variable_id__variable',
                values='value',
                aggfunc='first'
            )
        pivot_df = pivot_df.reset_index()
        pivot_df.columns.name = None
        return pivot_df
