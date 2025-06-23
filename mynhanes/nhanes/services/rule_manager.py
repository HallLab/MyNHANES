import os
from pathlib import Path
from nhanes.utils.logs import logger, start_logger
from django.conf import settings
from nhanes.models import RuleVariable


def create_rule_directory(rule, log):
    try:
        # base_dir = Path(str(rule.file_path)) / rule.rule
        base_dir = Path(settings.BASE_DIR) / "nhanes" / "rules" / rule.rule
        os.makedirs(base_dir, exist_ok=True)
    except Exception as e:
        logger(log, "e", f"Error creating directory: {e}")
        return False
    return True


def create_initial_files(rule, log):
    try:
        # base_dir = Path(str(rule.file_path)) / rule.rule
        base_dir = Path(settings.BASE_DIR) / "nhanes" / "rules" / rule.rule
        rule_file = base_dir / "rule.py"
        readme_file = base_dir / "rule.md"
        if rule_file.exists():
            msg = f"Rule file {rule_file} already exists."
            logger(log, "i", msg)
            return False

        # Criar as listas de tuplas para input_variables e output_variables
        input_variables = [
            (str(rv.version.version), "all datasets" if rv.dataset is None else str(rv.dataset.dataset), str(rv.variable.variable))  # noqa E501
            for rv in RuleVariable.objects.filter(type='i', rule=rule)
        ]
        output_variables = [
            (str(rv.version.version), "all datasets" if rv.dataset is None else str(rv.dataset.dataset), str(rv.variable.variable))  # noqa E501
            for rv in RuleVariable.objects.filter(type='o', rule=rule)
        ]

        # Converter as listas de tuplas para strings formatadas
        input_variables_str = ", ".join(
            [f"({v} / {d} / {var})" for v, d, var in input_variables]
            )
        output_variables_str = ", ".join(
            [f"({v} / {d} / {var})" for v, d, var in output_variables]
            )

        rule_file_content = f"""
from nhanes.workprocess.transformation_base import BaseTransformation
from nhanes.utils.logs import logger


class rule(BaseTransformation):
    \"""
    Rule Name: {rule.rule}
    Version: {rule.version}
    Description: {rule.description}

    This class applies the following transformations:
    (version / dataset / variable)
    - Input Variables: {input_variables_str}
    - Output Variables: {output_variables_str}

    The apply_normalization method should implement the logic for this rule.
    \"""

    def apply_transformation(self) -> bool:
        self.df_out = self.df_in.copy()

        msg = f"Starting normalization rule file to {{self.rule.rule}}"
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
        readme_content = f"""
# Rule Documentation: {rule.rule}

## Rule Information
- **Rule Name:** {rule.rule}
- **Version:** {rule.version}
- **Description:** {rule.description}
- **Status:** {"Active" if rule.is_active else "Inactive"}
- **Last Updated At:** {rule.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Repository URL:** [{rule.repo_url}]({rule.repo_url})

## Variables Involved
### Input Variables:
{input_variables}

### Output Variables:
{output_variables}

## Rule Explanation
Provide a detailed explanation of the rule here.

## Methodology
Explain the methodology used in this rule. Include any important details about the transformations applied, algorithms used, or special considerations.

## Supporting Literature
- [Link to Paper 1](https://example.com)
- [Link to Paper 2](https://example.com)

## Known Issues & Limitations
- Describe any known issues or limitations of this rule.

## Future Enhancements
- Describe any potential future enhancements or modifications that could improve the rule.

## Contact Information
- **Author:** [Your Name](mailto:your.email@example.com)
- **Project:** [Project Name](https://projecturl.com)
"""

        # write the rule file
        rule_file.write_text(rule_file_content.strip())
        readme_file.write_text(readme_content.strip())
    except Exception as e:
        msg = f"Error creating rule file: {e}"
        logger(log, "e", msg)

    return True


def setup_rule(rule):
    # start log monitor
    log_file = __name__
    log = start_logger(log_file)
    logger(log, "s", "Started the Rule Setup")

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
