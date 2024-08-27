import importlib
import pandas as pd
from nhanes.models import Rule, RuleVariable, Data, WorkProcessRule
from nhanes.utils.logs import logger, start_logger
# from django.db.models.query import QuerySet


class TransformationManager:

    def __init__(self, rules=None):
        # if isinstance(rules, QuerySet) and rules.model == Rule:
        #     self.rules = rules
        if isinstance(rules, Rule):
            # if unique rule, convert to list
            self.rules = [rules]
        elif isinstance(rules, str):
            # if string, filter the rule
            self.rules = Rule.objects.filter(rule=rules)
        elif isinstance(rules, list):
            if all(isinstance(rule, str) for rule in rules):
                # if list of strings, filter the rules
                self.rules = Rule.objects.filter(rule__in=rules)
            elif all(isinstance(rule, Rule) for rule in rules):
                # if list of Rule instances, use directly
                self.rules = rules
            else:
                raise ValueError(
                    "The list must contain only strings or instances of the Rule model."
                    )
        else:
            # if None or other type, get all active rules
            self.rules = Rule.objects.filter(is_active=True)

        # start logger
        self.log = start_logger('transformation_manager')

    def _get_input_data(self, qs_variable_in):
        df_list = []

        # get data for each rule variable
        for rule_var in qs_variable_in:
            # filter the Data model based on the (dataset, variable) pairs
            if rule_var.dataset:
                qs_df = Data.objects.filter(
                    version=rule_var.version,
                    dataset=rule_var.dataset,
                    variable=rule_var.variable
                ).values(
                    'version_id__version',
                    'cycle_id__cycle',
                    'dataset_id__dataset',
                    'sample',
                    'sequence',
                    'variable_id__variable',
                    'value',
                )
            else:
                qs_df = Data.objects.filter(
                    version=rule_var.version,
                    variable=rule_var.variable
                ).values(
                    'version_id__version',
                    'cycle_id__cycle',
                    'dataset_id__dataset',
                    'sample',
                    'sequence',
                    'variable_id__variable',
                    'value',
                )

            # convert queryset to dataframe
            data = list(qs_df)
            if data:  # check if there is data
                df = pd.DataFrame(data)
                df_list.append(df)

        # concatenate the dataframes
        if df_list:
            final_df = pd.concat(df_list, ignore_index=True)

            # change columns manes
            final_df.columns = [
                'version',
                'cycle',
                'dataset',
                'sample',
                'sequence',
                'variable',
                'value'
            ]
            # Pivot DataFrame final
            pivot_df = final_df.pivot_table(
                index=[
                    'version',
                    'cycle',
                    'dataset',
                    'sample',
                    'sequence'
                    ],
                columns='variable',
                values='value',
                aggfunc='first'
            )
            pivot_df = pivot_df.reset_index()
            pivot_df.columns.name = None

            return pivot_df
        else:
            # return empty dataframe if there is no data
            return pd.DataFrame()

    # INTERNAL FUNCTION
    def _update_work_process_rule(
            self,
            work_process_rule,
            status, log_msg,
            reset_attempt_count=False
            ):
        logger(self.log, "i" if status == 'complete' else "e", log_msg)
        work_process_rule.status = status
        work_process_rule.execution_logs = log_msg
        # work_process_rule.execution_time = 0
        if reset_attempt_count:
            work_process_rule.attempt_count = 0
        else:
            work_process_rule.attempt_count += 1
        work_process_rule.save()

    def apply_transformation(self):
        for rule in self.rules:

            msn = f"Applying transformation for rule {rule.rule}"
            logger(self.log, "s", msn)

            # get workprocess to rules
            work_process_rule = WorkProcessRule.objects.get(rule=rule)

            # check if work process rule is pending or error
            if work_process_rule.status not in ['pending', 'error']:
                self._update_work_process_rule(
                    work_process_rule,
                    work_process_rule.status,
                    f"Rule status is {work_process_rule.status}. Skip transformation"
                    )
                continue

            # check if the rule is already load on Data model
            if Data.objects.filter(rule_id=rule.id).first():
                self._update_work_process_rule(
                    work_process_rule,
                    'complete',
                    'transformation already applied. Delete the data to reapply',
                    reset_attempt_count=True
                    )
                continue

            # import the transformation dynamically based on the rule name
            module_name = f"nhanes.rules.{rule.rule}.rule"  # noqa E501

            transformation_module = importlib.import_module(module_name)

            # class needs to be the same name as the file
            class_name = 'rule'

            transformation_class = getattr(transformation_module, class_name)

            # querysets for target and source variables
            qs_variable_in = RuleVariable.objects.filter(rule=rule, type="i")
            qs_variable_out = RuleVariable.objects.filter(rule=rule, type="o")

            # load the input data from RawData
            df_in = self._get_input_data(qs_variable_in)

            # instantiate the transformation class
            transformation_instance = transformation_class(
                df_in=df_in,
                variable_out=qs_variable_out,
                rule=rule,
                log=self.log,
                )

            # START TRANSFORMATION WORKFLOW PROCESS
            try:
                steps = [
                    ('validate_input', "Input validation failed."),
                    ('set_data_type', "Variable type setting failed.", {'set': 'in'}),
                    ('apply_transformation', "Transformation failed."),
                    ('filter_output_columns', "Output filtering failed."),
                    ('set_data_type', "Variable type setting failed.", {'set': 'out'}),
                    ('validate_output', "Output validation failed."),
                    ('set_variable_type', "Variable type setting failed."),
                    ('save_data', "Data saving failed.")
                ]

                for step, error_message, *args in steps:
                    method = getattr(transformation_instance, step)
                    kwargs = args[0] if args else {}
                    if not method(**kwargs):
                        self._update_work_process_rule(
                            work_process_rule,
                            'error',
                            error_message
                            )
                        break
                else:
                    self._update_work_process_rule(
                        work_process_rule,
                        'complete',
                        'transformation completed successfully',
                        reset_attempt_count=True
                        )

            except Exception as e:
                msg = f"transformation failed: {e}"
                self._update_work_process_rule(work_process_rule, 'error', msg)
