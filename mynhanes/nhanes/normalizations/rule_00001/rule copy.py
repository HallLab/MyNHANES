from nhanes.workprocess.normalization_base import BaseNormalization
from nhanes.utils.logs import logger


class rule(BaseNormalization):
    """
    Rule Name: {rule_name}
    Version: {version}
    Description: {description}

    This class applies the following transformations:
    - Input Variables: {input_variables}
    - Output Variables: {output_variables}

    The apply_normalization method should implement the logic for this rule.
    """

    def apply_normalization(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to {self.rule.rule}"
        logger(self.log, "e", msg)

        # example transformation: Doubling the age
        self.df_out['IDADE'] = self.df_out['RIDAGEYR'] * 2

        return True
