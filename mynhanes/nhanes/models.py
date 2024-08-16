from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

v_version = "0.1.4"

# ----------------------------------------------------------------------------
# MODELS FOR MANAGING NHANES RAW DATA
# ----------------------------------------------------------------------------


# model represents a cycle of the NHANES.
class Cycle(models.Model):
    # cycle: The name of the cycle, should be unique.
    # base_dir: The base directory where data is stored.
    # year_code: The specific year code for NHANES, A, B, C, etc.
    # base_url: The base URL for the NHANES data.
    # dataset_url_pattern: The URL pattern for the datasets.
    # Garantir que não haja ciclos duplicados Ex. 2017-2018
    cycle = models.CharField(max_length=100, unique=True)
    base_dir = models.CharField(max_length=255, default="downloads")
    year_code = models.CharField(max_length=10, blank=True, null=True)
    base_url = models.URLField(default="https://wwwn.cdc.gov/Nchs/Nhanes")
    dataset_url_pattern = models.CharField(
        max_length=255,
        # default='%s/%s/%s_%s'
        default="%s/%s/%s",
    )

    def __str__(self):
        return self.cycle

    def get_dataset_url(self, file):
        return self.dataset_url_pattern % (self.base_url, self.cycle, file)

    class Meta:
        ordering = ["cycle"]
        # verbose_name = "01-Cycle"
        verbose_name_plural = "01-Cycles"


# model represents an entity in the NHANES study.
class Group(models.Model):
    group = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.group

    class Meta:
        # verbose_name = "02-Group"
        verbose_name_plural = "02-Group"


# model represents a file in the NHANES study.
class Dataset(models.Model):
    # name: The name of the dataset.
    # description: A description of the dataset.
    # is_download: A flag indicating if the dataset should be downloaded.
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
        verbose_name_plural = "03-Dataset"


# model represents a field in a dataset.
class Variable(models.Model):
    # variable: The Field Code of the field.
    # description: A description of the field.
    variable = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.variable} - ({self.description})"

    class Meta:
        # verbose_name = "04-Variable"
        verbose_name_plural = "04-Variable"


# model represents metadata for a field.
class VariableCycle(models.Model):
    # variable: The field the metadata is for.
    # cycle: The cycle the metadata is for.
    # variable_name: The name of the variable.
    # sas_label: The SAS label for the field.
    # english_text: The English text for the field.
    # target: The target of the field.
    # type: The type of the field.
    # value_table: The value table for the field.
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    variable_name = models.CharField(max_length=100)
    sas_label = models.CharField(max_length=100)
    english_text = models.TextField()
    target = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    value_table = models.JSONField()

    class Meta:
        unique_together = ("variable", "cycle")
        indexes = [
            models.Index(fields=["variable", "cycle"]),
        ]
        # verbose_name = "05-Variable by Cycle"
        verbose_name_plural = "05-Variable by Cycle"

    def __str__(self):
        return f"{self.variable_name} ({self.cycle.cycle})"


# model represents metadata for a dataset.
class DatasetCycle(models.Model):
    # dataset: The dataset the metadata is for.
    # cycle: The cycle the metadata is for.
    # metadata_url: The URL where the metadata can be found.
    # description: The description of the metadata.
    # has_special_year_code: A flag indicating if the dataset has a special year code.  # noqa E501
    # special_year_code: The specific year code for the dataset, if applicable.
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    metadata_url = models.URLField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    has_special_year_code = models.BooleanField(default=False)
    special_year_code = models.CharField(max_length=10, blank=True, null=True)
    has_dataset = models.BooleanField(default=False)

    class Meta:
        unique_together = ("dataset", "cycle")
        # verbose_name = "06-Donwload Control"
        verbose_name_plural = "06-Dataset by Cycle"

    def __str__(self):
        return f"{self.dataset.dataset} - {self.cycle.cycle}"


# model represents the data for a field in a dataset.
class RawData(models.Model):
    # cycle: The cycle the data is for.
    # dataset: The dataset the data is part of.
    # field: The field the data is for.
    # sample: The sample number.
    # value: The value of the data.
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    sample = models.IntegerField()
    sequence = models.IntegerField(default=0)
    value = models.CharField(max_length=255)

    class Meta:
        # verbose_name = "07-Data"
        verbose_name_plural = "07-Data"

    def __str__(self):
        return f"{self.cycle.cycle} | {self.dataset.dataset} | {self.variable.variable}"  # noqa: E501


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING QUERY STRUCTURE
# ----------------------------------------------------------------------------
class QueryColumns(models.Model):
    column_name = models.CharField(max_length=100, unique=True)
    internal_data_key = models.CharField(max_length=100, blank=True, null=True)
    column_description = models.CharField(max_length=255)

    def __str__(self):
        return self.column_name


class QueryStructure(models.Model):
    structure_name = models.CharField(max_length=100)
    columns = models.ManyToManyField("QueryColumns", related_name="query_columns")
    no_conflict = models.BooleanField(default=False)
    no_multi_index = models.BooleanField(default=False)

    def __str__(self):
        return self.structure_name

    class Meta:
        # verbose_name = "08-Query Structure"
        verbose_name_plural = "08-Query Structure"


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
        ("field__field", "Field Code"),
        ("field__description", "Field Name"),
        ("field__internal_id", "Field Internal Code"),
        ("field__internal_group", "Field Internal Group"),
        ("cycle__cycle", "Cycle"),
        ("dataset__group__group", "Group"),
        ("dataset__dataset", "Dataset Code"),
        ("dataset__description", "Dataset Name"),
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


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING NORMALIZATION DATA
# ----------------------------------------------------------------------------


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class Field(models.Model):
    FIELD_TYPES = (
        ("bin", "Binary"),
        ("cat", "Category"),
        ("num", "Numeric"),
        ("tex", "Text"),
        ("oth", "Other"),
    )
    field = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default="oth")
    tags = models.ManyToManyField(Tag, related_name="features", blank=True)

    class Meta:
        verbose_name = "Field"
        verbose_name_plural = "Field"

    def __str__(self):
        return self.field


class NormalizedData(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    sample = models.IntegerField()
    sequence = models.IntegerField(default=0)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Normalized Data"

    def __str__(self):
        return f"{self.cycle.cycle} | {self.dataset.dataset} | {self.field.field}"


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING THE NORMALIZATIONS PROCESS RULES
# ----------------------------------------------------------------------------


class NormalizationRule(models.Model):
    rule = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=20)
    folder_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    source_variables = models.ManyToManyField(Variable, related_name="source_for_rules")
    destination_fields = models.ManyToManyField(
        Field, related_name="destination_for_rules"
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("rule", "version")
        verbose_name_plural = "Normalization Rules"

    def __str__(self):
        return f"{self.rule} - {self.version}"


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING SYSTEM CONFIGURATION
# ----------------------------------------------------------------------------


# SystemConfig model represents the system configurations.
class SystemConfig(models.Model):
    # config_key: The key of the configuration.
    # config_value: The value of the configuration.
    config_key = models.CharField(max_length=100, unique=True)
    config_check = models.BooleanField(default=False)
    config_value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.config_key


# ----------------------------------------------------------------------------
# MODELS FOR MANAGING WORKFLOW CONTROL AND LOGGING
# ----------------------------------------------------------------------------


# DatasetControl model represents metadata for a dataset.
class WorkProcess(models.Model):
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
    chk_raw = models.BooleanField(
        default=False, verbose_name="Raw Data Ingested"
    )  # noqa E501
    chk_normalization = models.BooleanField(
        default=False, verbose_name="Normalization Data Ingested"
    )  # noqa E501
    system_version = models.CharField(max_length=15, default=v_version)
    time_download = models.IntegerField(default=0)
    time_raw = models.IntegerField(default=0)
    time_normalization = models.IntegerField(default=0)
    records_raw = models.IntegerField(default=0)
    records_normalization = models.IntegerField(default=0)
    n_samples = models.IntegerField(default=0)
    n_variables = models.IntegerField(default=0)

    class Meta:
        unique_together = ("dataset", "cycle")
        # verbose_name = "06-Donwload Control"
        verbose_name_plural = "Work Process"

    def __str__(self):
        return f"{self.dataset.dataset} - {self.cycle.cycle}"


class WorkProcessMasterData(models.Model):
    COMPONENT_CHOICES = (
        ("NormalizationRule", "Normalizations Rule"),
        ("Cycle", "Cycle"),
        ("Group", "Group"),
        ("Dataset", "Dataset"),
        ("Variable", "Variable"),
        ("DatasetCycle", "Dataset Cycle"),
        ("VariableCycle", "Variable Cycle"),
        ("Field", "Field"),
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
        verbose_name_plural = "Work Process Master Data"

    def __str__(self):
        return (
            f"Update for {self.get_component_type_display()} on {self.last_synced_at}"
        )


class Logs(models.Model):
    STATUS_CODE = (
        ("e", "Error"),
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
        verbose_name_plural = "Logs"

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

# ----------------------------------------------------------------------------
# Instantiate the models
__all__ = [
    "SystemConfig",
    "Cycle",
    "Group",
    "Dataset",
    "Variable",
    "VariableCycle",
    "RawData",
    "QueryStructure",
    "QueryColumns",
    "QueryFilter",
    "Tag",
    "Field",
    "NormalizedData",
]
