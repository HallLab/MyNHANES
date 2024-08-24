from nhanes.workprocess.normalization_base import BaseNormalization
from nhanes.utils.logs import logger


class rule(BaseNormalization):
    """
    Rule Name: rule_00003
    Version: 0.0.0
    Description: teste 3

    This class applies the following transformations:
    - Input Variables: RIDEXMON
    - Output Variables: RIDEXMON

    The apply_normalization method should implement the logic for this rule.
    """

    def apply_normalization(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to {rule.rule}"
        logger(self.log, "e", msg)

        # ----------------------------------------
        # START YOUR TRANSFORMATIONS HERE
        # ----------------------------------------

        # example transformation: Doubling the age
        # self.df_out['RIDAGEYR^2'] = self.df_out['RIDAGEYR'] * 2

        # ----------------------------------------
        # END YOUR TRANSFORMATIONS HERE
        # ----------------------------------------

        return True