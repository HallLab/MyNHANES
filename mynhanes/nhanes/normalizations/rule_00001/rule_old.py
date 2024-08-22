# transformations/transformation_1.py

from nhanes.workprocess.normalization_base import BaseNormalization
import pandas as pd


class rule(BaseNormalization):

    def apply_normalization(self) -> pd.DataFrame:
        """
        Doble the age

        Input: RIDAGEYR

        Output: Age

        """
        # method to ensure the correct type
        self.convert_to_type()

        # apply the transformation
        self.input_df['IDADE'] = self.input_df['RIDAGEYR'] * 4
        self.input_df['AGE2X'] = self.input_df['RIDAGEYR'] * 2

        # return the output
        return self.input_df[['IDADE', 'RIDAGEYR']]
    
        """
        Esse sera uma regra de normalizacao que ira dobrar a idade de exemplo,

        esse arquivo foi gerado quando criamos um novo registro no modelo Rule, que possui
        uma funcao para criar esse arquivo. precismos pensar em como poremos melhorar esse
        templante gerado, tipo adicionar um comentario com o nome da regra, input e output, exemplo:
        - o return deve ser um DataFrame com as colunas que serao usadas como variaveis alvo
        - o metodo apply_normalization é obrigatorio, adicionar um raise NotImplementedError caso nao seja implementado
        - o metodo validate_input herdado de BaseNormalization é opcional, mas pode ser implementado para validar o DataFrame de entrada
        - o metodo validate_output herdado de BaseNormalizationé opcional, mas pode ser implementado para validar o DataFrame de saida
        - copiar o self.iput_df para df_result e fazer as alteracoes necessarias
        - returnar o df_result com apenas os campos que serao usados como variaveis alvo
        """
    
    """
    Dentro do self.target_variable, temos uma queryset com informacoes sobre a variavel alvo.
    nela podemos interagir com os campos da variavel alvo, como por exemplo:
        for target in self.target_variable:
            target.variable_id
            target.dataset_id
            target.variable (object)
            target.dataset (object)
            target.variable.variable (nome da variavel)
            target.dataset.dataset (nome do dataset)
            target.rule (object)

    self.input_df é um DataFrame com os dados de entrada, onde as variaveis sao
    as colunas e as linhas sao os registros compostos de versao, cycle, dataset, sample sequence como
    caracteristicas do registro.


            
    Em Self temos:
        self.input_df: DataFrame de entrada
        self.output_df: DataFrame de saida
        self.target_variable: Variavel alvo

    Métodos:
        apply_normalization: Método
        validate_input: Método
        validate_output: Método
        execute: Método
        ensure_correct_type: Método
        convert_to_type: Método
        validate_output_variables: Método


        - 

    Importante ter sempre como saida um dataset com as colunas target:
    """
