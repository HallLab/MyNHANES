# transformations/base_transformation.py

from abc import ABC, abstractmethod
import pandas as pd
from nhanes.models import Variable, Data, Cycle, Dataset, Version


class BaseNormalization(ABC):

    def __init__(self, input_df: pd.DataFrame, target_variable=None):
        self.input_df = input_df
        self.output_df = None
        self.target_variable = target_variable or {}

    @abstractmethod
    def apply_normalization(self) -> pd.DataFrame:
        """
        Método abstrato que deve ser implementado por cada classe derivada.
        Deve aplicar a transformação e retornar um DataFrame resultante.
        """
        # pass
        raise NotImplementedError("Subclasses should implement this method.")

    def validate_input(self):
        """
        Método opcional para validar o DataFrame de entrada.
        """
        if self.input_df is None or self.input_df.empty:
            raise ValueError("O DataFrame de entrada está vazio ou é inválido.")

    def validate_output(self):
        """
        Método opcional para validar o DataFrame de saída.
        """
        if self.output_df is None or self.output_df.empty:
            raise ValueError("O DataFrame de saída está vazio ou é inválido.")

    def validate_output_variables(self):
        """
        Valida se todas as variáveis de destino estão presentes e têm os tipos corretos.
        """
        missing_variables = []
        for rule_variable in self.target_variable:
            if rule_variable.variable.variable not in self.output_df.columns:
                missing_variables.append(rule_variable.variable.variable)
            else:
                # Ensure the type is correct (expand this as needed)
                expected_type = rule_variable.variable.type
                actual_type = self.output_df[rule_variable.variable.variable].dtype
                if expected_type == 'num' and not pd.api.types.is_numeric_dtype(actual_type):
                    raise ValueError(f"Variable {rule_variable.variable.variable} expected to be numeric but got {actual_type}")
                # Add more type checks as needed

        if missing_variables:
            raise ValueError(
                f"As seguintes variáveis de destino estão ausentes no DataFrame resultante: {', '.join(missing_variables)}"
            )
        else:
            print("Todas as variáveis de destino estão presentes no DataFrame resultante com os tipos corretos.")

    # def execute(self) -> pd.DataFrame:
    #     """
    #     Executa a transformação após validar a entrada.
    #     """
    #     self.validate_input()
    #     self.output_df = self.apply_normalization()
    #     self.validate_output()
    #     return self.output_df
    def execute(self) -> bool:
        """
        Executes the normalization process.

        Returns True if successful, False otherwise.
        """
        try:
            self.validate_input()
            success = self.apply_normalization()
            if success:
                self.validate_output()
                return True
            else:
                return False
        except Exception as e:
            print(f"Normalization failed: {e}")
            return False

    def filter_output_columns(self) -> pd.DataFrame:
        """
        Filtra as colunas do output_df para incluir apenas as variáveis de destino e as colunas-chave.
        """
        # Lista de colunas-chave que devem sempre estar presentes
        key_columns = ['version', 'cycle', 'dataset', 'sample', 'sequence']

        # Extrair as variáveis de destino do self.target_variable queryset
        target_columns = [rule_variable.variable.variable for rule_variable in self.target_variable]

        # Verifica se todas as colunas-chave estão presentes no DataFrame
        missing_keys = [col for col in key_columns if col not in self.output_df.columns]
        if missing_keys:
            raise ValueError(f"As seguintes colunas-chave estão ausentes: {', '.join(missing_keys)}")

        # Filtra o DataFrame para incluir apenas as colunas-chave e de destino
        self.output_df = self.output_df[key_columns + target_columns]

        return self.output_df

    def ensure_correct_type(self):
        for column in self.input_df.columns:
            field_type = self.field_type_map.get(column, 'oth')
            if field_type in ['num', 'bin']:
                self.input_df[column] = pd.to_numeric(
                    self.input_df[column],
                    errors='coerce'
                    )
            elif field_type == 'cat':
                self.input_df[column] = self.input_df[column].astype(str)
            # Add more type handling as needed

    # trabalhando com os dados de entrada
    def convert_to_type(self):
        """
        Analisa e converte os tipos de dados das colunas do input_df para o tipo mais adequado.    # noqa E501
        """
        for variable in self.input_df.columns:
            inferred_type = self.infer_type(self.input_df[variable])
            self.input_df[variable] = self.apply_conversion(self.input_df[variable], inferred_type)  # noqa E501

    def infer_type(self, series):
        """
        Infere o tipo de dado mais adequado para uma série do pandas.
        """
        # Verifica se a série pode ser convertida para float
        if pd.to_numeric(series, errors='coerce').notnull().all():
            return 'float'
        # Verifica se a série pode ser convertida para int
        elif pd.to_numeric(series, errors='coerce').dropna().apply(float.is_integer).all():  # noqa E501
            return 'int'
        # Verifica se a série tem um número pequeno de valores únicos, sugerindo uma categoria  # noqa E501
        elif series.nunique() < 0.1 * len(series):
            return 'category'
        # Se for texto, retorna string
        elif series.apply(lambda x: isinstance(x, str)).all():
            return 'string'
        else:
            return 'object'

    def apply_conversion(self, series, inferred_type):
        """
        Converte uma série do pandas para o tipo de dado inferido.
        """
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

    # ---- WORK AREA ----
    # load the data types
    def field_type(self):
        """
        Applies the normalization and returns the result DataFrame.
        """

        # update Field types if necessary
        for qry in self.target_variable:
            if qry.variable.type == 'oth':
                variable = Variable.objects.get(variable=qry.variable)
                inferred_type = self._infer_type(self.input_df[qry.variable.variable])
                variable.type = inferred_type
                variable.save()
        # return only target fields
        return True

    # helper methods: maybe move to a utility or BaseNormalization class
    def _infer_type(self, series):
        """
        Infers the FIELD_TYPE of the series (e.g., 'num', 'bin', 'cat', 'tex', 'oth').
        """
        # check if the column is binary, i.e., has two distinct values besides NaN
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


    def save_output_data(self, rule):
        """
        Saves the transformed data in the Data model.
        """
        # Assuming self.output_df is already prepared by apply_normalization()
        if self.output_df is None or self.output_df.empty:
            raise ValueError("Output DataFrame is empty or not defined.")

        qry_version = Version.objects.get(version="normalized")
        cycle_map = {cycle.id: cycle for cycle in Cycle.objects.filter(id__in=self.output_df['cycle'].unique())}
        dataset_map = {dataset.id: dataset for dataset in Dataset.objects.filter(id__in=self.output_df['dataset'].unique())}

        normalized_data_instances = []

        for _, row in self.output_df.iterrows():
            cycle_instance = cycle_map[row['cycle']]
            dataset_instance = dataset_map[row['dataset']]

            for rule_variable in self.target_variable:
                normalized_data_instances.append(
                    Data(
                        version=qry_version,
                        cycle=cycle_instance,
                        dataset=dataset_instance,
                        variable=rule_variable.variable,
                        sample=row['sample'],
                        sequence=row['sequence'],
                        value=row[rule_variable.variable.variable],
                        rule_id=rule,
                    )
                )

        Data.objects.bulk_create(normalized_data_instances)
        return True
