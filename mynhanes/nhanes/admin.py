import json
from django.contrib import admin, messages
from django.utils.html import format_html
from .models import (
    Version,
    Cycle,
    Group,
    Dataset,
    Variable,
    VariableCycle,
    DatasetCycle,
    Data,
    QueryColumns,
    QueryStructure,
    QueryFilter,
    Tag,
    Rule,
    RuleVariable,
    WorkProcessNhanes,
    WorkProcessRule,
    WorkProcessMasterData,
    Logs,
)
from nhanes.services import query
# from django.urls import path
# from django.http import HttpResponseRedirect
# from django.core.management import call_command
# from django.contrib import messages
from nhanes.reports import report_variables, report_datasetcycle, report_variablecycle

from django import forms
# from django.urls import reverse
# from django.utils.safestring import mark_safe
from nhanes.services.rule_manager import setup_rule
from nhanes.workprocess.transformation_manager import TransformationManager
# from nhanes.utils.start_jupyter import start_jupyter_notebook
# from django.shortcuts import redirect
# from django.urls import path
from nhanes.workprocess.ingestion_nhanes import ingestion_nhanes
from django.contrib.admin import SimpleListFilter

# ----------------------------------
# NHANES ADMIN
# ----------------------------------


class VersionAdmin(admin.ModelAdmin):
    model = Version


class CycleAdmin(admin.ModelAdmin):
    list_display = ("cycle", "year_code", "dataset_url_pattern")


class GroupAdmin(admin.ModelAdmin):
    model = Group


class DatasetAdmin(admin.ModelAdmin):
    list_display = ("group_name", "dataset", "description")
    list_filter = ("group__group",)
    search_fields = ("dataset", "description", "group__group")

    def get_queryset(self, request):
        # This function serves to optimize the loading of queries
        queryset = super().get_queryset(request)
        return queryset.select_related("group")

    def group_name(self, obj):
        return obj.group.group


class VariableAdmin(admin.ModelAdmin):
    list_display = (
        "variable",
        "description",
        "is_active",
        "type",
        "show_tags",
    )
    list_display_links = ("variable", "description")
    search_fields = ("variable", "description")
    list_filter = ("tags", "type")
    filter_horizontal = ("tags",)
    actions = [
        'report_selected',
        'report_all',
        ]

    def show_tags(self, obj):
        return ", ".join([tag.tag for tag in obj.tags.all()])

    show_tags.short_description = 'Tags'

    def report_selected(self, request, queryset):
        return report_variables.report_selected_variables(self, request, queryset)

    def report_all(self, request, queryset):
        return report_variables.report_all_variables(self, request, queryset)

    report_selected.short_description = "Generate report for selected variables"
    report_all.short_description = "Generate report for all variables"


class VariableCycleAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "cycle",
        "dataset",
        "variable_name",
        "sas_label",
        "type",
        # "english_text",
        "formatted_value_table",
    )
    search_fields = ("variable_name", "sas_label", "english_text", "value_table")
    list_filter = ("version", "cycle", "dataset", "type", "dataset_id__group", "variable_id__tags")  # noqa: E501
    actions = [
        'report_selected',
        'report_all',
    ]

    def formatted_value_table(self, obj):
        # Assume that obj.value_table is the JSON field
        try:
            data = json.loads(obj.value_table)
            html = '<table border="1">'
            html += "<tr><th>Code or Value</th><th>Value Description</th><th>Count</th><th>Cumulative</th><th>Skip to Item</th></tr>"  # noqa: E501
            for item in data:
                html += f"<tr><td>{item.get('Code or Value')}</td><td>{item.get('Value Description')}</td><td>{item.get('Count')}</td><td>{item.get('Cumulative')}</td><td>{item.get('Skip to Item')}</td></tr>"  # noqa: E501
            html += "</table>"
            return format_html(html)
        except json.JSONDecodeError:
            return "Invalid JSON"

    formatted_value_table.short_description = "Value Table"

    def report_selected(self, request, queryset):
        return report_variablecycle.report_selected_variable_cycles(self, request, queryset)  # noqa E501

    def report_all(self, request, queryset):
        return report_variablecycle.report_all_variable_cycles(self, request, queryset)

    report_selected.short_description = "Generate report for selected Variables Cycles"
    report_all.short_description = "Generate report for all Variables Cycles"


class DatasetCycleAdmin(admin.ModelAdmin):
    list_display = ('cycle', 'dataset', 'dataset_name', 'has_dataset', 'metadata_url',) #  'has_special_year_code', 'special_year_code')  # TODO: RETORN LINK WEB # noqa E501
    search_fields = ('dataset__dataset', 'cycle__cycle', 'metadata_url')
    list_filter = ('cycle', 'dataset', 'has_special_year_code', 'has_dataset', 'dataset__group__group')  # noqa E501
    list_editable = ('has_dataset', )
    ordering = ('cycle__cycle', 'dataset__dataset',)
    actions = [
        'report_selected',
        'report_all',
        ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('dataset', 'cycle')
        return queryset

    def group_name(self, obj):
        return obj.dataset.group.group

    def dataset_name(self, obj):
        return obj.dataset.description

    def report_selected(self, request, queryset):
        return report_datasetcycle.report_selected_dataset_cycles(self, request, queryset)  # noqa E501

    def report_all(self, request, queryset):
        return report_datasetcycle.report_all_dataset_cycles(self, request, queryset)

    report_selected.short_description = "Generate report for selected Dataset Cycles"
    report_all.short_description = "Generate report for all Dataset Cycles"


class DataAdmin(admin.ModelAdmin):
    list_display = ('version', 'cycle', 'dataset', 'variable', 'sample', 'sequence', 'rule_id', 'value')  # noqa E501
    search_fields = ('dataset__dataset', 'cycle__cycle', 'variable__variable', 'value')
    list_filter = ('cycle', 'dataset', 'version', 'variable')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('version', 'dataset', 'cycle', 'variable')
        return queryset


class TagAdmin(admin.ModelAdmin):
    list_display = ("tag", "description")


# ----------------------------------
# QUERY ADMIN
# ----------------------------------


class QueryColumnAdmin(admin.ModelAdmin):
    list_display = ("column_name", "internal_data_key", "column_description")
    search_fields = ("column_name", "column_description")


class QueryFilterInline(admin.TabularInline):
    model = QueryFilter
    extra = 0  # define number of extra forms to display


class QueryStructureAdmin(admin.ModelAdmin):
    list_display = ("structure_name", "no_conflict", "no_multi_index")
    list_editable = (
        "no_conflict",
        "no_multi_index",
    )
    search_fields = ("structure_name",)
    filter_horizontal = ("columns",)
    inlines = [QueryFilterInline]
    actions = [query.download_data_report]


# ----------------------------------
# TRANSFORMATION ADMIN
# ----------------------------------

@admin.action(description='Setup Rule Directories and Files')
def setup_rules(modeladmin, request, queryset):
    for rule in queryset:
        try:
            # call rule_manager
            result = setup_rule(rule)
            if result:
                messages.success(
                    request,
                    f"Files for rule '{rule.rule}' created successfully."
                    )
            else:
                messages.warning(
                    request,
                    f"Files for rule '{rule.rule}' already exist."
                    )
        except Exception as e:
            messages.error(
                request,
                f"Error creating files for rule '{rule.rule}': {str(e)}"
                )
# setup_rules.short_description = "Generate rule files"


class RuleVariableForm(forms.ModelForm):
    class Meta:
        model = RuleVariable
        fields = '__all__'


class RuleVariableAdmin(admin.ModelAdmin):
    form = RuleVariableForm
    list_display = ('rule', 'variable', 'dataset')


class RuleVariableInline(admin.TabularInline):
    model = RuleVariable
    extra = 1
    autocomplete_fields = ['variable', 'dataset']
    verbose_name = "Variable Mapping"
    verbose_name_plural = "Variable Mappings"


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['rule'].initial = Rule().generate_rule_name()


class RuleAdmin(admin.ModelAdmin):
    form = RuleForm
    list_display = ('rule', 'version', 'is_active', 'repo_url_link')  # 'open_jupyter_link')  # noqa: E501
    search_fields = ('rule', 'description')
    list_filter = ('is_active', 'updated_at')
    inlines = [RuleVariableInline]
    actions = [setup_rules]

    def repo_url_link(self, obj):
        if obj.repo_url:
            return format_html(
                '<a href="{}" target="_blank">Documentation</a>', obj.repo_url
                )
        return "No Documentation"

    repo_url_link.short_description = "Documentation"

    # # controler to ensure that Jupyter starts only once
    # jupyter_started = False

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if not RuleAdmin.jupyter_started:
    #         start_jupyter_notebook()
    #         RuleAdmin.jupyter_started = True

    # def open_jupyter_link(self, obj):
    #     link = f"http://127.0.0.1:8888/edit/nhanes/normalizations/{obj.rule}/{obj.file_script}" # noqa: E501
    #     return mark_safe(f'<a href="{link}" target="_blank">Edit in Jupyter</a>')

    # open_jupyter_link.short_description = "Edit in Jupyter"


# ----------------------------------
# WORK PROCESS ADMIN
# ----------------------------------


# @admin.register(WorkProcessMasterData)
class WorkProcessMasterDataAdmin(admin.ModelAdmin):
    list_display = ('component_type', 'last_synced_at', 'source_file_version', 'status')
    list_filter = ('component_type', 'status', 'last_synced_at')
    search_fields = ('component_type', 'source_file_version')
    ordering = ('-last_synced_at',)
    fields = ('component_type', 'last_synced_at', 'source_file_version', 'status')
    readonly_fields = ('last_synced_at',)

    # show the display of the component type and status
    def get_component_type_display(self, obj):
        return obj.get_component_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    get_component_type_display.short_description = 'Component Type'
    get_status_display.short_description = 'Status'


class LogsAdmin(admin.ModelAdmin):
    model = Logs


class HasDatasetFilter(SimpleListFilter):
    title = 'Has Dataset'  # ou qualquer título que você desejar
    parameter_name = 'has_dataset'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(datasetcycle__has_dataset=True)
        if self.value() == 'no':
            return queryset.filter(datasetcycle__has_dataset=False)


class WorkProcessNhanesAdmin(admin.ModelAdmin):
    list_display = (
        'cycle_name',
        'group_name',
        'dataset_name',
        'has_dataset_status',
        'status',
        'is_download',
        )
    list_filter = (
        'cycle',
        'status',
        HasDatasetFilter,
        'is_download',
        'dataset__group__group'
        )
    list_editable = ('status', 'is_download',)
    search_fields = ('dataset__dataset', 'cycle__cycle')
    raw_id_fields = ('dataset', 'cycle')
    # actions = [download_nhanes_files]
    actions = [
        'set_status_pending',
        'set_status_standby',
        'set_status_delete',
        'set_download_true',
        'set_download_false',
        'run_ingestion_data',
        ]

    def dataset_name(self, obj):
        return obj.dataset.dataset

    def cycle_name(self, obj):
        return obj.cycle.cycle

    def group_name(self, obj):
        return obj.dataset.group.group

    @admin.display(boolean=True, description='Has Dataset')
    def has_dataset_status(self, obj):
        return obj.datasetcycle.has_dataset

    # shorting by related fields
    dataset_name.admin_order_field = 'dataset__dataset'
    cycle_name.admin_order_field = 'cycle__cycle'
    group_name.admin_order_field = 'dataset__group__group'

    def get_queryset(self, request):
        # perform a prefetch_related to load the related group
        queryset = super().get_queryset(request)
        return queryset.select_related('dataset', 'cycle', 'dataset__group')

    # def metadata_url_link(self, obj):
    #     if obj.metadata_url:
    #         return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.metadata_url)  # noqa: E501
    #     else:
    #         return "Dataset does not exist"
    # metadata_url_link.short_description = 'no file'  # noqa: E501

    def set_status_pending(self, request, queryset):
        rows_updated = queryset.update(status='standby')
        if rows_updated == 1:
            message_bit = "1 work process nhanes was"
        else:
            message_bit = f"{rows_updated} work process nhanes were"
        self.message_user(request, f"{message_bit} successfully marked as standby.")

    def set_status_standby(self, request, queryset):
        rows_updated = queryset.update(status='pending')
        if rows_updated == 1:
            message_bit = "1 work process nhanes was"
        else:
            message_bit = f"{rows_updated} work process nhanes were"
        self.message_user(request, f"{message_bit} successfully reset to pending.")

    def set_status_delete(self, request, queryset):
        rows_updated = queryset.delete()
        if rows_updated == 1:
            message_bit = "1 work process nhanes was"
        else:
            message_bit = f"{rows_updated} work process nhanes were"
        self.message_user(request, f"{message_bit} successfully deleted.")

    def set_download_true(self, request, queryset):
        rows_updated = queryset.update(is_download=True)
        if rows_updated == 1:
            message_bit = "1 work process nhanes was"
        else:
            message_bit = f"{rows_updated} work process nhanes were"
        self.message_user(request, f"{message_bit} successfully marked as download.")

    def set_download_false(self, request, queryset):
        rows_updated = queryset.update(is_download=False)
        if rows_updated == 1:
            message_bit = "1 work process nhanes was"
        else:
            message_bit = f"{rows_updated} work process nhanes were"
        self.message_user(request, f"{message_bit} successfully marked as not download.")  # noqa: E501

    def run_ingestion_data(self, request, queryset):
        # for work_process_nhanes in queryset:
        #     work_process_nhanes.run_ingestion_data()
        ingestion_nhanes()
        self.message_user(request, "Ingestion data process started.")

    set_status_pending.short_description = "Set selected workprocess as standby"
    set_status_standby.short_description = "Set selected workprocess to pending"
    set_status_delete.short_description = "Set selected workprocess to delete"
    set_download_true.short_description = "Set selected workprocess as download"
    set_download_false.short_description = "Set selected workprocess as not download"
    run_ingestion_data.short_description = "Run all ingestion data process"


class WorkProcessRuleAdmin(admin.ModelAdmin):
    list_display = (
        'rule',
        'status',
        'last_synced_at',
        'attempt_count'
        )
    list_filter = ('status', 'last_synced_at')
    search_fields = ('rule__rule',)
    readonly_fields = ('last_synced_at', 'execution_time', 'attempt_count')
    actions = [
        'set_complete',
        'set_standby',
        'set_pending',
        'run_rule_data',
        'drop_rule_data'
        ]

    def set_complete(self, request, queryset):
        rows_updated = queryset.update(status='complete')
        if rows_updated == 1:
            message_bit = "1 work process rule was"
        else:
            message_bit = f"{rows_updated} work process rules were"
        self.message_user(request, f"{message_bit} successfully marked as complete.")

    def set_standby(self, request, queryset):
        rows_updated = queryset.update(status='standby')
        if rows_updated == 1:
            message_bit = "1 work process rule was"
        else:
            message_bit = f"{rows_updated} work process rules were"
        self.message_user(request, f"{message_bit} successfully marked as standby.")

    def set_pending(self, request, queryset):
        rows_updated = queryset.update(status='pending')
        if rows_updated == 1:
            message_bit = "1 work process rule was"
        else:
            message_bit = f"{rows_updated} work process rules were"
        self.message_user(request, f"{message_bit} successfully reset to pending.")

    def run_rule_data(self, request, queryset):
        selected_rules = queryset.values_list('rule', flat=True)
        qs_rules = Rule.objects.filter(id__in=selected_rules)
        list_rules = list(qs_rules.values_list('rule', flat=True))
        manager = TransformationManager(rules=list_rules)
        manager.apply_transformation()
        msg = f"Normalization applied for {len(list_rules)} selected rules."
        self.message_user(request, msg)

    def drop_rule_data(modeladmin, request, queryset):
        for work_process_rule in queryset:
            # drop all data associated with the rule in the Data table
            Data.objects.filter(rule_id=work_process_rule.rule).delete()
            # update the status of the WorkProcessRule to 'pending'
            msg = "Data deleted and status reset to pending."
            work_process_rule.status = 'pending'
            work_process_rule.execution_logs = msg
            work_process_rule.save()
        modeladmin.message_user(request, msg)

    set_complete.short_description = "Set selected rules as complete"
    set_standby.short_description = "Set selected rules as standby"
    set_pending.short_description = "set selected rules to pending"
    run_rule_data.short_description = "Run selected rules"
    drop_rule_data.short_description = "Delete data and reset rule status"


admin.site.register(WorkProcessRule, WorkProcessRuleAdmin)
admin.site.register(Cycle, CycleAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Variable, VariableAdmin)
admin.site.register(VariableCycle, VariableCycleAdmin)
admin.site.register(DatasetCycle, DatasetCycleAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(QueryColumns, QueryColumnAdmin)
admin.site.register(QueryStructure, QueryStructureAdmin)
# admin.site.register(QueryFilter, QueryFilterAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleVariable, RuleVariableAdmin)
admin.site.register(WorkProcessNhanes, WorkProcessNhanesAdmin)
admin.site.register(WorkProcessMasterData, WorkProcessMasterDataAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(Version, VersionAdmin)
