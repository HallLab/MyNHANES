# import os
# from pathlib import Path
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.parameters import config

# from django.conf import settings

v_version = config['global']['version']
rule_seq = config['transformations']['rule_seq']


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING NHANES MASTER DATA
# ----------------------------------------------------------------------------


class Version(models.Model):
    version = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.version

    class Meta:
        verbose_name_plural = "MasterData: Versions"


# model represents a cycle of the NHANES.
class Cycle(models.Model):
    cycle = models.CharField(max_length=100, unique=True)
    year_code = models.CharField(max_length=10, blank=True, null=True)
    base_url = models.URLField(default="https://wwwn.cdc.gov/Nchs/Nhanes")
    dataset_url_pattern = models.CharField(
        max_length=255,
        # default='%s/%s/%s_%s'
        default="%s/%s",
    )

    def __str__(self):
        return self.cycle

    def get_dataset_url(self, file):
        # return self.dataset_url_pattern % (self.base_url, self.cycle, file)
        return self.dataset_url_pattern % (self.base_url, file)

    class Meta:
        ordering = ["cycle"]
        # verbose_name = "01-Cycle"
        verbose_name_plural = "MasterData: Cycles"


# model represents an entity in the NHANES study.
class Group(models.Model):
    group = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.group

    class Meta:
        # verbose_name = "02-Group"
        verbose_name_plural = "MasterData: Groups"


# model represents a file in the NHANES study.
class Dataset(models.Model):
    dataset = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.dataset} ({self.group})"

    class Meta:
        # Define a constraint that ensures that each dataset
        # is unique within a specific group
        unique_together = ("dataset", "group")
        # verbose_name = "03-Dataset"
        verbose_name_plural = "MasterData: Dataset"


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "MasterData: Tags"


class Variable(models.Model):
    TYPES = (
        ("bin", "Binary"),
        ("cat", "Category"),
        ("num", "Numeric"),
        ("tex", "Text"),
        ("oth", "Other"),
    )
    variable = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=TYPES, default="oth")
    tags = models.ManyToManyField(Tag, related_name="features", blank=True)

    class Meta:
        verbose_name = "Variable"
        verbose_name_plural = "MasterData: Variable"

    def __str__(self):
        return self.variable


class VariableCycle(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    variable_name = models.CharField(max_length=100)
    sas_label = models.CharField(max_length=100)
    english_text = models.TextField()
    target = models.TextField()
    type = models.CharField(max_length=100)
    value_table = models.JSONField(null=True, blank=True)  # TODO: Nao pode ter null

    class Meta:
        unique_together = ("version", "variable", "cycle", "dataset")
        indexes = [
            models.Index(fields=["variable", "cycle"]),
        ]
        verbose_name_plural = "Moviment: Variable by Cycle"

    def __str__(self):
        return f"{self.variable_name} ({self.cycle.cycle})"

    # def save(self, *args, **kwargs):
    #     # Substituir NaN por None para evitar erro
    #     if self.value_table is None or pd.isna(self.value_table):
    #         self.value_table = None
    #     super().save(*args, **kwargs)


class DatasetCycle(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    metadata_url = models.URLField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    observation = models.TextField(blank=True, null=True)
    has_special_year_code = models.BooleanField(default=False)
    special_year_code = models.CharField(max_length=10, blank=True, null=True)
    has_dataset = models.BooleanField(default=False)

    class Meta:
        unique_together = ("dataset", "cycle")
        verbose_name_plural = "Moviment: Dataset by Cycle"

    def __str__(self):
        return f"{self.dataset.dataset} - {self.cycle.cycle}"


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING THE NORMALIZATIONS PROCESS RULES
# ----------------------------------------------------------------------------


class Rule(models.Model):
    rule = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    repo_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ("rule", "version")
        verbose_name_plural = "Transformations: Rules"

    def __str__(self):
        return f"{self.rule} - {self.version}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.rule = self.generate_rule_name()
        super().save(*args, **kwargs)

        self.check_or_create_work_process_rule()

    def generate_rule_name(self):
        # last_rule = Rule.objects.all().order_by('id').last()
        # if not last_rule:
        #     return "rule_00001"
        # rule_number = int(last_rule.rule.split('_')[-1]) + 1
        # return f"rule_{rule_number:05d}"
        if rule_seq == 'global':
            prefix = 'rule_'
            start_range = 1
            end_range = 499999
        elif rule_seq == 'local':
            prefix = 'rule_'
            start_range = 500000
            end_range = 999999
        else:
            raise ValueError("Invalid rule_seq value in config file")

        last_rule = Rule.objects.filter(
            rule__regex=f'^{prefix}[0-9]{{5}}$',
            rule__gte=f'{prefix}{start_range:05d}',
            rule__lte=f'{prefix}{end_range:05d}'
        ).order_by('id').last()

        if not last_rule:
            return f"{prefix}{start_range:05d}"

        last_rule_number = int(last_rule.rule.split('_')[-1])
        next_rule_number = last_rule_number + 1

        if next_rule_number > end_range:
            raise ValueError("No more available rule numbers in the current range")

        return f"{prefix}{next_rule_number:05d}"

    def check_or_create_work_process_rule(self):
        work_process_rule, created = WorkProcessRule.objects.get_or_create(rule=self)
        if created:
            work_process_rule.status = "pending"
            work_process_rule.execution_logs = "new rule created"
            work_process_rule.save()
        return work_process_rule


class RuleVariable(models.Model):
    TYPES = (
        ("i", "in"),
        ("o", "out"),
    )
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)
    dataset = models.ForeignKey(
        'Dataset',
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    type = models.CharField(max_length=1, choices=TYPES, default="i")

    class Meta:
        verbose_name_plural = "Transformations: Rules Variables"

    def __str__(self):
        if self.dataset:
            return f"{self.rule.rule} - {self.type}: {self.variable.variable} in {self.dataset.dataset}"  # noqa E501
        else:
            return f"{self.rule.rule} - {self.type}: {self.variable.variable} in All Datasets"  # noqa E501


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING THE MOVIMENT DATA
# ----------------------------------------------------------------------------


class Data(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    sample = models.IntegerField()
    sequence = models.IntegerField(default=0)
    rule_id = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
        )
    value = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['sample', 'variable', 'cycle', 'dataset', 'version']),
        ]
        verbose_name_plural = "Moviment: Data"

    def __str__(self):
        return f"Sample {self.sample} | Variable {self.variable.variable} | Cycle {self.cycle.cycle} | Dataset {self.dataset.dataset} | Version {self.version}"  # noqa E501


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING QUERY STRUCTURE
# ----------------------------------------------------------------------------


class QueryColumns(models.Model):
    column_name = models.CharField(max_length=100, unique=True)
    internal_data_key = models.CharField(max_length=100, blank=True, null=True)
    column_description = models.CharField(max_length=255)

    def __str__(self):
        return self.column_name

    class Meta:
        verbose_name_plural = "Query: Columns"


class QueryStructure(models.Model):
    structure_name = models.CharField(max_length=100)
    columns = models.ManyToManyField("QueryColumns", related_name="query_columns")
    no_conflict = models.BooleanField(default=False)
    no_multi_index = models.BooleanField(default=False)

    def __str__(self):
        return self.structure_name

    class Meta:
        # verbose_name = "08-Query Structure"
        verbose_name_plural = "Query: Structure"


class QueryFilter(models.Model):
    OPERATOR_CHOICES = (
        ("eq", "Equal"),
        ("ne", "Not Equal"),
        ("lt", "Less Than"),
        ("lte", "Less Than or Equal"),
        ("gt", "Greater Than"),
        ("gte", "Greater Than or Equal"),
        ("contains", "Contains"),
        ("icontains", "Contains (Case-Insensitive)"),
        ("exact", "Exact"),
        ("iexact", "Exact (Case-Insensitive)"),
        ("in", "In"),
        ("startswith", "Starts With"),
        ("istartswith", "Starts With (Case-Insensitive)"),
        ("endswith", "Ends With"),
        ("iendswith", "Ends With (Case-Insensitive)"),
        ("isnull", "Search For Null Values"),
        ("search", "Search"),
        ("regex", "Use Regular Expression"),
        ("iregex", "Use Regular Expression (Case-Insensitive)"),
        ("file", "Path to csv file with each value in a line"),
    )
    DIMENSION_CHOICES = (
        ("variable__variable", "Variable Code"),
        ("variable__description", "Variable Name"),
        ("cycle__cycle", "Cycle"),
        ("dataset__group__group", "Group"),
        ("dataset__dataset", "Dataset Code"),
        ("dataset__description", "Dataset Name"),
        ("version__version", "Version"),
        ("variable__tags__tag", "Tag"),
    )
    query_structure = models.ForeignKey(
        QueryStructure, related_name="filters", on_delete=models.CASCADE
    )
    filter_name = models.CharField(
        max_length=30, choices=DIMENSION_CHOICES, default="variable"
    )
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, default="eq")
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.filter_name} {self.operator} {self.value}"

    class Meta:
        # verbose_name = "08-Query Structure"
        verbose_name_plural = "Query: Filters"


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING WORKFLOW CONTROL AND LOGGING
# ----------------------------------------------------------------------------


# DatasetControl model represents metadata for a dataset.
class WorkProcessNhanes(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("complete", "Complete"),
        ("error", "Error"),
        ("delete", "Delete"),
        ("standby", "Stand By"),
        ("no_file", "No File"),
    )
    datasetcycle = models.ForeignKey(DatasetCycle, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    is_download = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    last_synced_at = models.DateTimeField(auto_now=True, verbose_name="Last Update")
    source_file_version = models.CharField(
        max_length=500, null=True, blank=True, default=""
    )
    source_file_size = models.BigIntegerField(default=0)
    system_version = models.CharField(max_length=15, default=v_version)
    time_download = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    records = models.IntegerField(default=0)
    n_samples = models.IntegerField(default=0)
    n_variables = models.IntegerField(default=0)

    class Meta:
        unique_together = ("dataset", "cycle")
        # verbose_name = "06-Donwload Control"
        verbose_name_plural = "Workprocess: NHANES"

    def __str__(self):
        return f"{self.dataset.dataset} - {self.cycle.cycle}"


class WorkProcessMasterData(models.Model):
    COMPONENT_CHOICES = (
        ("Version", "Version"),
        ("Cycle", "Cycle"),
        ("Group", "Group"),
        ("Dataset", "Dataset"),
        ("Tag", "Tag"),
        ("Variable", "Variable"),
        ("VariableTag", "Variable Tag"),
        ("DatasetCycle", "Dataset Cycle"),
        ("VariableCycle", "Variable Cycle"),
        ("Rule", "Rule"),
        ("RuleVariable", "Rule Variable"),
        ("QueryColumns", "Query Columns"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("complete", "Complete"),
        ("error", "Error"),
        ("delete", "Delete"),
        ("standby", "Stand By"),
        ("no_file", "No File"),
    )
    component_type = models.CharField(
        max_length=20,
        choices=COMPONENT_CHOICES,
        unique=True
        )
    last_synced_at = models.DateTimeField(auto_now_add=True)
    source_file_version = models.CharField(
        max_length=500, null=True, blank=True, default=""
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        verbose_name_plural = "Workprocess: MasterData"

    def __str__(self):
        return (
            f"Update for {self.get_component_type_display()} on {self.last_synced_at}"
        )


class WorkProcessRule(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("complete", "Complete"),
        ("error", "Error"),
        ("delete", "Delete"),
        ("standby", "Stand By"),
    )
    rule = models.OneToOneField(Rule, on_delete=models.CASCADE)
    last_synced_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    execution_logs = models.TextField(null=True, blank=True)
    execution_time = models.DurationField(null=True, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Workprocess: Transformations"

    # def __str__(self):
    #     return (
    #         f"Update for {self.get_component_type_display()} on {self.last_synced_at}"
    #     )


class Logs(models.Model):
    STATUS_CODE = (
        ("e", "Error"),
        ("i", "Information"),
        ("w", "Warning"),
        ("s", "Success"),
    )
    # Campos para relacionamento genérico
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    system_version = models.CharField(max_length=15, default=v_version)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CODE, default="s")
    description = models.TextField(null=True, blank=True, default=None)

    class Meta:
        verbose_name_plural = "Workprocess: Logs"

    def __str__(self):
        return f"{self.get_status_display()} - {self.content_type} - {self.created_at}"


""" To use logs, you need to import the ContentType model from Django:
from django.contrib.contenttypes.models import ContentType
from myapp.models import WorkProcessMasterData, WorkProcess, Logs

master_data = WorkProcessMasterData.objects.get(id=1)
log = Logs.objects.create(
    content_type=ContentType.objects.get_for_model(WorkProcessMasterData),
    object_id=master_data.id,
    status='e',
    description='Failed to sync data from GitHub',

workprocess = WorkProcess.objects.get(id=1)
log = Logs.objects.create(
    content_type=ContentType.objects.get_for_model(WorkProcess),
    object_id=workprocess.id,
    status='s',
    description='Process completed successfully',

)"""
