import importlib
import pandas as pd
from nhanes.models import Rule, RuleVariable, Data, WorkProcessRule
from nhanes.utils.logs import logger, start_logger


class TransformationManager:

    def __init__(self, rules=None):
        # self.rules = Rule.objects.filter(is_active=True)
        self.rules = rules if rules else Rule.objects.filter(is_active=True)
        self.log = start_logger('transformation_manager')

    # INTERNAL FUNCTION
    def _get_input_data(self, qs_variable_in):
        # filter the Data model based on the (dataset, variable) pairs
        # TODO: improve to get the compose key version-dataset-variable
        qs_df = Data.objects.filter(
            dataset_id__in=qs_variable_in.values_list('dataset_id', flat=True),
            variable_id__in=qs_variable_in.values_list('variable_id', flat=True)
        ).values(
            'version',
            'cycle',
            'dataset',
            'sample',
            'sequence',
            'variable',
            'variable_id__variable',
            'value',
        )
        # convert queryset to dataframe
        data = list(qs_df)
        df = pd.DataFrame(data)

        # pivot the dataFrame
        pivot_df = df.pivot_table(
                index=['version', 'cycle', 'dataset', 'sample', 'sequence'],
                columns='variable_id__variable',
                values='value',
                aggfunc='first'
            )
        pivot_df = pivot_df.reset_index()
        pivot_df.columns.name = None
        return pivot_df

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

    def apply_transformations(self):
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
