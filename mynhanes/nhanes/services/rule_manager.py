import os
from pathlib import Path
from nhanes.utils.logs import logger, start_logger


def create_rule_directory(rule, log):
    try:
        base_dir = Path(str(rule.file_path)) / rule.rule
        os.makedirs(base_dir, exist_ok=True)
    except Exception as e:
        logger(log, "e", f"Error creating directory: {e}")
        return False
    return True


def create_initial_files(rule, log):
    try:
        base_dir = Path(str(rule.file_path)) / rule.rule
        rule_file = base_dir / rule.file_script
        if rule_file.exists():
            msg = f"Rule file {rule_file} already exists."
            logger(log, "i", msg)
            return False

        input_variables = ", ".join(
            rule.rulevariable_set.filter(is_source=True)
            .values_list('variable__variable', flat=True)
        )
        output_variables = ", ".join(
            rule.rulevariable_set.filter(is_source=False)
            .values_list('variable__variable', flat=True)
        )

        rule_file_content = f"""
from nhanes.workprocess.normalization_base import BaseNormalization
from nhanes.utils.logs import logger


class rule(BaseNormalization):
    \"""
    Rule Name: {rule.rule}
    Version: {rule.version}
    Description: {rule.description}

    This class applies the following transformations:
    - Input Variables: {input_variables}
    - Output Variables: {output_variables}

    The apply_normalization method should implement the logic for this rule.
    \"""

    def apply_normalization(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to {{rule.rule}}"
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

"""
        # write the rule file
        rule_file.write_text(rule_file_content.strip())
    except Exception as e:
        msg = f"Error creating rule file: {e}"
        logger(log, "e", msg)

    return True


def setup_rule(rule):
    # start log monitor
    log_file = __name__
    log = start_logger(log_file)
    logger(log, "s", "Started the Rule Setup")

    # check if the rule has a file path
    if not rule.file_path:
        msg = f"Rule {rule} does not have a file path. Creating one."
        logger(log, "e", msg)
        return False

    # create the rule directory
    if not create_rule_directory(rule, log):
        msg = f"Error creating directory for rule {rule}."
        logger(log, "e", msg)
        return False

    if not create_initial_files(rule, log):
        msg = f"Error creating initial files for rule {rule}."
        logger(log, "e", msg)
        return False

    msg = f"Rule {rule} setup completed."
    logger(log, "s", msg)
    return True
