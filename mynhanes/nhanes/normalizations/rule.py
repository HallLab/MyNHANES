from nhanes.workprocess.normalization_base import BaseNormalization
from nhanes.utils.logs import logger


class rule(BaseNormalization):
    """
    Rule Name: rule_00002
    Version: 0.0.0
    Description: teste

    This class applies the following transformations:
    - Input Variables: RIDAGEYR, IDADE
    - Output Variables: 

    The apply_normalization method should implement the logic for this rule.
    """

    def apply_normalization(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to rule_00002"
        logger(self.log, "e", msg)

        # example transformation: Doubling the age
        self.df_out['RIDAGEYR^2'] = self.df_out['RIDAGEYR'] * 2

        return True