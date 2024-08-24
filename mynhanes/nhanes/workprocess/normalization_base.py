import pandas as pd
from abc import ABC, abstractmethod
from django.db.models.query import QuerySet
from nhanes.models import Variable, Data, Cycle, Dataset, Version, Rule
from nhanes.utils.logs import logger


class BaseNormalization(ABC):

    def __init__(self, df_in: pd.DataFrame, variable_out, rule, log):
        self.df_in = df_in
        self.df_out = None
        self.variable_out = variable_out
        self.rule = rule
        self.log = log
        # self.log = start_logger(f"{self.rule.rule}_normalization")

    @abstractmethod
    def apply_normalization(self) -> pd.DataFrame:
        msg = "Subclasses should implement this method."
        logger(self.log, "e", msg)

    def validate_input(self) -> bool:
        if self.df_in is None or self.df_in.empty:
            msm = "The input DataFrame is empty or invalid."
            logger(self.log, "i", msm)
            return False

        if not isinstance(self.variable_out, QuerySet):
            msm = "variable_out needs to be a queryset."
            logger(self.log, "i", msm)
            return False

        if not isinstance(self.rule, Rule):
            msm = "Rule needs to be an instance of the Rule model."
            logger(self.log, "i", msm)
            return False

        return True

    def validate_output(self) -> bool:
        if self.df_out is None or self.df_out.empty:
            msm = "The output DataFrame is empty or invalid."
            logger(self.log, "i", msm)
            return False

        missing_variables = []
        for rule_variable in self.variable_out:
            if rule_variable.variable.variable not in self.df_out.columns:
                missing_variables.append(rule_variable.variable.variable)
            else:
                # Ensure the type is correct (expand this as needed)
                expected_type = rule_variable.variable.type
                actual_type = self.df_out[rule_variable.variable.variable].dtype
                if expected_type == 'num' and not pd.api.types.is_numeric_dtype(actual_type): # noqa E501
                    msm = f"Variable {rule_variable.variable.variable} expected to be numeric but got {actual_type}" # noqa E501
                    logger(self.log, "i", msm)
                    return False

        if missing_variables:
            msm = f"The following target variables are missing from the output DataFrame: {', '.join(missing_variables)}" # noqa E501
            logger(self.log, "i", msm)
            return False

        return True

    def filter_output_columns(self) -> bool:
        key_columns = ['version', 'cycle', 'dataset', 'sample', 'sequence']
        target_columns = [
            rule_variable.variable.variable for rule_variable in self.variable_out
            ]
        # check if all key columns are present in the DataFrame
        missing_keys = [col for col in key_columns if col not in self.df_out.columns]
        if missing_keys:
            msm = f"The following key columns are missing: {', '.join(missing_keys)}"
            logger(self.log, "i", msm)
            return False
        # filter the DataFrame to include only the key and target columns
        self.df_out = self.df_out[key_columns + target_columns]
        return True

    def set_data_type(self, set='in') -> bool:
        try:
            if set == 'in':
                for variable in self.df_in.columns:
                    inferred_type = self._infer_type(self.df_in[variable])
                    self.df_in[variable] = self._apply_conversion(
                        self.df_in[variable],
                        inferred_type
                        )
            elif set == 'out':
                for variable in self.df_out.columns:
                    inferred_type = self._infer_type(self.df_out[variable])
                    self.df_out[variable] = self._apply_conversion(
                        self.df_out[variable],
                        inferred_type
                        )
        except Exception as e:
            msm = f"Failed to set data type: {e}"
            logger(self.log, "e", msm)
            return False
        return True

    def _infer_type(self, series):
        if pd.to_numeric(series, errors='coerce').notnull().all():
            return 'float'
        elif pd.to_numeric(series, errors='coerce').dropna().apply(float.is_integer).all():  # noqa E501
            return 'int'
        elif series.nunique() < 0.1 * len(series):
            return 'category'
        elif series.apply(lambda x: isinstance(x, str)).all():
            return 'string'
        else:
            return 'object'

    def _apply_conversion(self, series, inferred_type):
        if inferred_type == 'float':
            return pd.to_numeric(series, errors='coerce')
        elif inferred_type == 'int':
            return pd.to_numeric(series, errors='coerce').astype('Int64')
        elif inferred_type == 'category':
            return series.astype('category')
        elif inferred_type == 'string':
            return series.astype('str')
        else:
            return series

    def set_variable_type(self) -> bool:
        for qry in self.variable_out:
            if qry.variable.type == 'oth':
                try:
                    variable = Variable.objects.get(variable=qry.variable)
                    inferred_type = self._infer_variable_type(
                        self.df_in[qry.variable.variable]
                        )
                    variable.type = inferred_type
                    variable.save()
                except Exception as e:
                    msm = f"Failed to set variable type: {e}"
                    logger(self.log, "e", msm)
                    continue
        return True

    def _infer_variable_type(self, series):
        unique_values = series.dropna().unique()
        if len(unique_values) == 2:
            return 'bin'  # Binary
        if pd.api.types.is_bool_dtype(series):
            return 'bin'  # Binary
        elif pd.api.types.is_numeric_dtype(series):
            return 'num'  # Numeric
        elif pd.api.types.is_categorical_dtype(series) or series.nunique() < 0.1 * len(series):  # noqa E501
            return 'cat'  # Category
        elif pd.api.types.is_string_dtype(series):
            return 'tex'  # Text
        return 'oth'  # Other

    def save_data(self) -> bool:
        if self.df_out is None or self.df_out.empty:
            msm = "Output DataFrame is empty or not defined."
            logger(self.log, "i", msm)

        qry_version = Version.objects.get(version="normalized")

        cycle_map = {
            cycle.id: cycle for cycle in Cycle.objects.filter(
                id__in=self.df_out['cycle'].unique()
                )
            }
        dataset_map = {
            dataset.id: dataset for dataset in Dataset.objects.filter(
                id__in=self.df_out['dataset'].unique()
                )
            }

        normalized_data_instances = []

        for _, row in self.df_out.iterrows():
            cycle_instance = cycle_map[row['cycle']]
            dataset_instance = dataset_map[row['dataset']]

            for rule_variable in self.variable_out:
                normalized_data_instances.append(
                    Data(
                        version=qry_version,
                        cycle=cycle_instance,
                        dataset=dataset_instance,
                        variable=rule_variable.variable,
                        sample=row['sample'],
                        sequence=row['sequence'],
                        value=row[rule_variable.variable.variable],
                        rule_id=self.rule,
                    )
                )
        try:
            Data.objects.bulk_create(normalized_data_instances)
        except Exception as e:
            msm = f"Failed to save data: {e}"
            logger(self.log, "e", msm)
            return False

        return True
