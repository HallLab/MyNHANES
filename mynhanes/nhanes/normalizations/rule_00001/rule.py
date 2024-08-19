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
        self.input_df['AGE'] = self.input_df['RIDAGEYR']
        self.input_df['AGE2X'] = self.input_df['RIDAGEYR'] * 2

        # return the output
        return self.input_df[['AGE', 'AGE2X']]
