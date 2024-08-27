from nhanes.workprocess.transformation_base import BaseTransformation
from nhanes.utils.logs import logger


class rule(BaseTransformation):
    """
    Rule Name: rule_00002
    Version: 0.0.0
    Description: Define Participants with Parkinson's disease by medication

    This class applies the following transformations:
    (version / dataset / variable)
    - Input Variables: (nhanes / RXQ_RX / RXDDRGID)
    - Output Variables: (normalized / all datasets / PD_BY_DRUG)

    The apply_normalization method should implement the logic for this rule.
    """

    def apply_transformation(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to {self.rule.rule}"
        logger(self.log, "e", msg)

        # ----------------------------------------
        # START YOUR TRANSFORMATIONS HERE
        # ----------------------------------------

        # Medications for Parkinson's disease
        # d03473: CARBIDOPA; LEVODOPA

        # Medications for Parkinson's disease
        ls_drug = ["d03473", ]

        # Create a boolean column indicating PD_BY_DRUG
        self.df_out["PD_BY_DRUG"] = self.df_out["RXDDRGID"].isin(ls_drug)

        # Filter only records where PD_BY_DRUG is True
        self.df_out = self.df_out[self.df_out["PD_BY_DRUG"]]

        # Drop the columns 'sequence' and 'RXDDRGID'
        self.df_out = self.df_out.drop(['sequence', 'RXDDRGID'], axis=1)

        # Drop duplicates
        self.df_out = self.df_out.drop_duplicates()

        # Reset the 'sequence' column to 0
        self.df_out['sequence'] = 0

        # Change the version to 'normalized'
        self.df_out['version'] = 'normalized'

        # NOTE: keep dataset?

        # ----------------------------------------
        # END YOUR TRANSFORMATIONS HERE
        # ----------------------------------------

        return True
