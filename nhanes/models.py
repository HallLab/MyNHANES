from django.db import models


# SystemConfig model represents the system configurations.
class SystemConfig(models.Model):
    # config_key: The key of the configuration.
    # config_value: The value of the configuration.
    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.BooleanField(default=False)

    def __str__(self):
        return self.config_key


# Cycle model represents a cycle of the NHANES study.
class Cycle(models.Model):
    # cycle: The name of the cycle, should be unique.
    # base_dir: The base directory where data is stored.
    # year_code: The specific year code for NHANES, A, B, C, etc.
    # base_url: The base URL for the NHANES data.
    # dataset_url_pattern: The URL pattern for the datasets.
    # Garantir que não haja ciclos duplicados Ex. 2017-2018
    cycle = models.CharField(max_length=100, unique=True)
    base_dir = models.CharField(max_length=255, default='downloads')
    year_code = models.CharField(max_length=10, blank=True, null=True)
    base_url = models.URLField(default='https://wwwn.cdc.gov/Nchs/Nhanes')
    dataset_url_pattern = models.CharField(
        max_length=255,
        # default='%s/%s/%s_%s'
        default='%s/%s/%s'
        )

    def __str__(self):
        return self.cycle

    def get_dataset_url(self, file):
        return self.dataset_url_pattern % (
            self.base_url,
            self.cycle,
            file
            # dataset,
            # self.year_code
            )

    class Meta:
        ordering = ['cycle']

# https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.htm


# Group model represents an entity in the NHANES study.
class Group(models.Model):
    group = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.group


# Dataset model represents a dataset in the NHANES study.
class Dataset(models.Model):
    # name: The name of the dataset.
    # description: A description of the dataset.
    # is_download: A flag indicating if the dataset should be downloaded.
    dataset = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
        )

    def __str__(self):
        return f"{self.dataset} ({self.group})"

    class Meta:
        # Define a constraint that ensures that each dataset
        # is unique within a specific group
        unique_together = ('dataset', 'group')


# DatasetControl model represents metadata for a dataset.
class DatasetControl(models.Model):
    # dataset: The dataset the metadata is for.
    # cycle: The cycle the metadata is for.
    # metadata_url: The URL where the metadata can be found.
    # description: The description of the metadata.
    # has_special_year_code: A flag indicating if the dataset has a special year code.  # noqa E501
    # special_year_code: The specific year code for the dataset, if applicable.
    # is_download: A flag indicating if the dataset should be downloaded.
    # status: The status of the dataset metadata (pending, complete, error, delete).  # noqa E501
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('error', 'Error'),
        ('delete', 'Delete'),
        ('standby', 'Stand By'),
        ('no_file', 'No File'),
    )
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    metadata_url = models.URLField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    has_special_year_code = models.BooleanField(default=False)
    special_year_code = models.CharField(max_length=10, blank=True, null=True)
    is_download = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
        )

    class Meta:
        unique_together = ('dataset', 'cycle')

    def __str__(self):
        return f"{self.dataset.dataset} - {self.cycle.cycle}"


# Field model represents a field in a dataset.
class Field(models.Model):
    # name: The Field Code of the field.
    # internal_id: The internal ID of the field.
    # description: A description of the field.
    field = models.CharField(max_length=100, unique=True)
    internal_id = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.field} - ({self.description})"


# FieldCycle model represents metadata for a field.
class FieldCycle(models.Model):
    # field: The field the metadata is for.
    # cycle: The cycle the metadata is for.
    # variable_name: The name of the variable.
    # sas_label: The SAS label for the field.
    # english_text: The English text for the field.
    # target: The target of the field.
    # type: The type of the field.
    # value_table: The value table for the field.
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    variable_name = models.CharField(max_length=100)
    sas_label = models.CharField(max_length=100)
    english_text = models.TextField()
    target = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    value_table = models.JSONField()

    class Meta:
        unique_together = ('field', 'cycle')

    def __str__(self):
        return f"{self.variable_name} ({self.cycle.cycle})"


# NHANESData model represents the data for a field in a dataset.
class Data(models.Model):
    # cycle: The cycle the data is for.
    # dataset: The dataset the data is part of.
    # field: The field the data is for.
    # sample: The sample number.
    # value: The value of the data.
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    sample = models.IntegerField()
    value = models.CharField(max_length=255)

    # class Meta:
    #     # Definindo os índices compostos e garantindo a unicidade
    #     unique_together = (('cycle', 'dataset', 'field', 'sample'),)
    #     indexes = [
    #         models.Index(fields=['cycle', 'dataset', 'field', 'sample']),
    # ]

    def __str__(self):
        return f"{self.cycle.cycle} | {self.dataset.dataset} | {self.field.field}"  # noqa: E501


# Querys Domains
class QueryColumns(models.Model):
    column_name = models.CharField(max_length=100, unique=True)
    internal_data_key = models.CharField(max_length=100, blank=True, null=True)
    column_description = models.CharField(max_length=255)

    def __str__(self):
        return self.column_name


class QueryStructure(models.Model):
    structure_name = models.CharField(max_length=100)
    columns = models.ManyToManyField(
        'QueryColumns',
        related_name='query_columns'
        )
    no_conflict = models.BooleanField(default=False)
    no_multi_index = models.BooleanField(default=False)

    def __str__(self):
        return self.structure_name


class QueryFilter(models.Model):
    OPERATOR_CHOICES = (
        ('eq', 'Equal'),
        ('ne', 'Not Equal'),
        ('lt', 'Less Than'),
        ('lte', 'Less Than or Equal'),
        ('gt', 'Greater Than'),
        ('gte', 'Greater Than or Equal'),
        ('contains', 'Contains'),
        ('icontains', 'Contains (Case-Insensitive)'),
        ('exact', 'Exact'),
        ('iexact', 'Exact (Case-Insensitive)'),
        ('in', 'In'),
        ('startswith', 'Starts With'),
        ('istartswith', 'Starts With (Case-Insensitive)'),
        ('endswith', 'Ends With'),
        ('iendswith', 'Ends With (Case-Insensitive)'),
        ('isnull', 'Search For Null Values'),
        ('search', 'Search'),
        ('regex', 'Use Regular Expression'),
        ('iregex', 'Use Regular Expression (Case-Insensitive)'),
    )
    DIMENSION_CHOICES = (
        ('field__field', 'Field Code'),
        ('field__description', 'Field Name'),
        ('field__internal_id', 'Field Internal Code'),
        ('cycle__cycle', 'Cycle'),
        ('dataset__group', 'Group'),
        ('dataset__dataset', 'Dataset Code'),
        ('dataset__description', 'Dataset Name'),
    )
    query_structure = models.ForeignKey(
        QueryStructure,
        related_name='filters',
        on_delete=models.CASCADE
        )
    filter_name = models.CharField(
        max_length=20,
        choices=DIMENSION_CHOICES,
        default='field_id'
        )
    operator = models.CharField(
        max_length=20,
        choices=OPERATOR_CHOICES,
        default='eq'
        )
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.filter_name} {self.operator} {self.value}"
