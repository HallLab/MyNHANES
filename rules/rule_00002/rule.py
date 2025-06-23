from nhanes.workprocess.transformation_base import BaseTransformation
from nhanes.utils.logs import logger


class rule(BaseTransformation):
    """
    Rule Name: rule_00002
    Version: 1.0
    Description: This rule identifies participants who use medications associated with
    cholesterol management and adjusts their LDL and total cholesterol levels to values
    that would be expected without medication use. The rule generates a new variable
    identifying these participants and provides the adjusted LDL and total cholesterol
    variables in the Normalized dataset.

    Distribution of Samples with use one of these drugs:

    - ATORVASTATIN_CALCIUM
    - SIMVASTATIN
    - PRAVASTATIN_SODIUM
    - FLUVASTATIN_SODIUM

    # LDL and TC values are reduced by 30% and 20% respectively for participants who
    # use medications for cholesterol control.


    This class applies the following transformations:
    (version / dataset / variable)
    - Input Variables:
        (nhanes / RXQ_RX / RXDDRGID),
        (nhanes / all datasets / LBDLDL),
        (nhanes / all datasets / LBXTC)
    - Output Variables:
        (normalized / all datasets / LBDLDL_WO_DRUG),
        (normalized / all datasets / LBXTC_WO_DRUG),
        (normalized / all datasets / USE_CHOLESTEROL_DRUG)

    The apply_normalization method should implement the logic for this rule.
    """

    def apply_transformation(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to {self.rule.rule}"
        logger(self.log, "e", msg)

        # ----------------------------------------
        # START YOUR TRANSFORMATIONS HERE
        # ----------------------------------------

        # Medications for Cholesterol control
        # d04105: ATORVASTATIN CALCIUM
        # d00746: SIMVASTATIN
        # d07805: SIMVASTATIN; SITAGLIPTIN (NOTE: Need Check)
        # d00348: PRAVASTATIN SODIUM
        # d03183: FLUVASTATIN SODIUM

        # List of medications for cholesterol control
        ls_drug = ["d04105", "d00746", "d07805", "d00348", "d03183"]

        # Create a bool col indicating participants who use medications for cholesterol
        self.df_out["USE_CHOLESTEROL_DRUG"] = self.df_out["RXDDRGID"].isin(ls_drug)

        # LDL and TC values are reduced by 30% and 20% respectively
        self.df_out['LBDLDL_WO_DRUG'] = self.df_out.apply(
            lambda row: row['LBDLDL'] / 0.7 if row['USE_CHOLESTEROL_DRUG'] else row['LBDLDL'], axis=1  # noqa E501
        )
        self.df_out['LBXTC_WO_DRUG'] = self.df_out.apply(
            lambda row: row['LBXTC'] / 0.8 if row['USE_CHOLESTEROL_DRUG'] else row['LBXTC'], axis=1  # noqa E501
        )

        # Drop the sources columns
        self.df_out = self.df_out.drop(
            ['sequence', 'RXDDRGID', 'LBDLDL', 'LBXTC'],
            axis=1
            )

        # Drop duplicates
        self.df_out = self.df_out.drop_duplicates()
        self.df_out['sequence'] = 0

        # Target as normalized version
        self.df_out['version'] = 'normalized'

        # ----------------------------------------
        # END YOUR TRANSFORMATIONS HERE
        # ----------------------------------------

        return True
