# transformations/transformation_1.py

from nhanes.workprocess.normalization_base import BaseNormalization


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
        """
        Apply normalization transformations.

        This method modifies self.output_df and returns True if successful.
        """

        # Ensuring correct types for the input variables
        self.convert_to_type()

        # Create a copy of the input DataFrame to work with
        self.output_df = self.input_df.copy()

        # Example transformation: Doubling the age
        self.output_df['IDADE'] = self.output_df['RIDAGEYR'] * 2

        # Validate that all output variables are present
        self.validate_output_variables()

        # Filter the output DataFrame to include only the target columns
        self.filter_output_columns()

        # If everything went well, return True
        return True
