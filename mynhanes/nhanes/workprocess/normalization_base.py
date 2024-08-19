# transformations/base_transformation.py

from abc import ABC, abstractmethod
import pandas as pd
from nhanes.models import Field, NormalizedData, Cycle, Dataset


class BaseNormalization(ABC):

    def __init__(self, input_df: pd.DataFrame, destination_fields=None):
        self.input_df = input_df
        self.output_df = None
        self.destination_fields = destination_fields or {}

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

    def execute(self) -> pd.DataFrame:
        """
        Executa a transformação após validar a entrada.
        """
        self.validate_input()
        self.output_df = self.apply_normalization()
        self.validate_output()
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
        for field_name, field_type in self.destination_fields.items():
            if field_type == 'oth':
                field = Field.objects.get(field=field_name)
                inferred_type = self._infer_type(self.input_df[field_name])
                field.field_type = inferred_type
                field.save()
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

    # save the output data in NormalizedData
    def save_output_data(self):
        """
        Salva os dados transformados no modelo NormalizedData.
        """
        output_df = self.input_df

        # Pré-carregar todas as instâncias de Cycle e Dataset necessárias
        cycle_ids = output_df['cycle'].unique()
        dataset_ids = output_df['dataset'].unique()

        cycle_map = {
            cycle.id: cycle for cycle in Cycle.objects.filter(
                id__in=cycle_ids
                )
            }
        dataset_map = {
            dataset.id: dataset for dataset in Dataset.objects.filter(
                id__in=dataset_ids
                )
            }

        # Pré-carregar o campo de destino uma vez
        field_map = {
            field.field: field for field in Field.objects.filter(
                field__in=self.destination_fields.keys())
                }

        # Lista para armazenar instâncias de NormalizedData a serem criadas em batch
        normalized_data_instances = []

        for _, row in output_df.iterrows():
            cycle_instance = cycle_map[row['cycle']]
            dataset_instance = dataset_map[row['dataset']]

            for field_name in self.destination_fields:
                normalized_data_instances.append(
                    NormalizedData(
                        cycle=cycle_instance,
                        dataset=dataset_instance,
                        field=field_map[field_name],
                        sample=row['sample'],
                        sequence=row['sequence'],
                        value=row[field_name]
                    )
                )

        NormalizedData.objects.bulk_create(normalized_data_instances)
