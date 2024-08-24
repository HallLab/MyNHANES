import os
import json
from pathlib import Path
from django.conf import settings
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
    SystemConfig,
    Data,
    # QueryColumns,
    # QueryStructure,
    # QueryFilter,
    Tag,
    Rule,
    RuleVariable,
    WorkProcess,
    WorkProcessRule,
    WorkProcessMasterData,
    Logs,
)
# from nhanes.services import query
# from django.urls import path
# from django.http import HttpResponseRedirect
# from django.core.management import call_command
# from django.contrib import messages

from django import forms
# from django.urls import reverse
from django.utils.safestring import mark_safe
from nhanes.services.rule_manager import setup_rule
from nhanes.workprocess.normalization_manager import NormalizationManager
from nhanes.utils.start_jupyter import start_jupyter_notebook
from django.shortcuts import redirect
from django.urls import path


class VersionAdmin(admin.ModelAdmin):
    model = Version


class CycleAdmin(admin.ModelAdmin):
    list_display = ("cycle", "year_code", "base_dir", "dataset_url_pattern")


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
    )
    search_fields = ("variable", "description")


class VariableCycleAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "cycle",
        "variable_name",
        "sas_label",
        "type",
        "english_text",
        "formatted_value_table",
    )

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

    search_fields = ("variable_name", "sas_label", "english_text", "value_table")


class DatasetCycleAdmin(admin.ModelAdmin):
    model = DatasetCycle


class SystemConfigAdmin(admin.ModelAdmin):
    model = SystemConfig


class DataAdmin(admin.ModelAdmin):
    model = Data


class TagAdmin(admin.ModelAdmin):
    model = Tag


# # class NormalizedDataAdmin(admin.ModelAdmin):
# #     model = NormalizedData
# @admin.register(NormalizedData)
# class NormalizedDataAdmin(admin.ModelAdmin):
#     list_display = ('cycle', 'dataset', 'field', 'sample', 'sequence', 'value')

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('reset-normalizationdata/', self.reset_normalizationdata),
#         ]
#         return custom_urls + urls

#     def reset_normalizationdata(self, request):
#         try:
#             call_command('reset_normalizationdata')
#             self.message_user(request, 'All data and auto-increment ID for NormalizedData have been reset.', messages.SUCCESS)  # noqa E501
#         except Exception as e:
#             self.message_user(request, f'Error: {str(e)}', messages.ERROR)
#         return HttpResponseRedirect("../")


# class RuleAdmin(admin.ModelAdmin):
#     model = Rule


# class WorkProcessMasterDataAdmin(admin.ModelAdmin):
#     model = WorkProcessMasterData
# @admin.register(WorkProcessMasterData)
class WorkProcessMasterDataAdmin(admin.ModelAdmin):
    list_display = ('component_type', 'last_synced_at', 'source_file_version', 'status')
    list_filter = ('component_type', 'status', 'last_synced_at')
    search_fields = ('component_type', 'source_file_version')
    ordering = ('-last_synced_at',)
    fields = ('component_type', 'last_synced_at', 'source_file_version', 'status')
    readonly_fields = ('last_synced_at',)

    # Exibição detalhada dos registros
    def get_component_type_display(self, obj):
        return obj.get_component_type_display()

    def get_status_display(self, obj):
        return obj.get_status_display()

    get_component_type_display.short_description = 'Component Type'
    get_status_display.short_description = 'Status'


class WorkProcessAdmin(admin.ModelAdmin):
    list_display = (
        'cycle_name',
        'group_name',
        'dataset_name',
        'status',
        'is_download',
        )
    list_filter = ('cycle', 'status', 'is_download', 'dataset__group__group')
    list_editable = ('status', 'is_download',)
    search_fields = ('dataset__dataset', 'cycle__cycle')
    raw_id_fields = ('dataset', 'cycle')
    # actions = [download_nhanes_files]

    def dataset_name(self, obj):
        return obj.dataset.dataset

    def cycle_name(self, obj):
        return obj.cycle.cycle

    def group_name(self, obj):
        return obj.dataset.group.group

    # Shorting by related fields
    dataset_name.admin_order_field = 'dataset__dataset'
    cycle_name.admin_order_field = 'cycle__cycle'
    group_name.admin_order_field = 'dataset__group__group'

    def get_queryset(self, request):
        # Perform a prefetch_related to load the related group
        queryset = super().get_queryset(request)
        return queryset.select_related('dataset', 'cycle', 'dataset__group')

    # def metadata_url_link(self, obj):
    #     if obj.metadata_url:
    #         return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.metadata_url)  # noqa: E501
    #     else:
    #         return "Dataset does not exist"
    # metadata_url_link.short_description = 'no file'  # noqa: E501


class LogsAdmin(admin.ModelAdmin):
    model = Logs


# class QueryColumnAdmin(admin.ModelAdmin):
#     list_display = ("column_name", "internal_data_key", "column_description")
#     search_fields = ("column_name", "column_description")


# class QueryFilterInline(admin.TabularInline):
#     model = QueryFilter
#     extra = 0  # Define number of extra forms to display


# class QueryStructureAdmin(admin.ModelAdmin):
#     list_display = ("structure_name", "no_conflict", "no_multi_index")
#     list_editable = (
#         "no_conflict",
#         "no_multi_index",
#     )
#     search_fields = ("structure_name",)
#     # Easy access to the filters
#     filter_horizontal = ("columns",)
#     # Add filters to the QueryStructure page
#     inlines = [QueryFilterInline]
#     # Add actions to the QueryStructure page
#     # actions = [download_query_results]
#     actions = [query.download_data_report]


# ----------------------------------
# Transformations Rule Admin
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


# TODO: A funcionalizade de filtro dimaninco nao esta funcionando em admin
# TODO: tirar a opcap de selecionar a pasta, deixar fixa na normalizacao

class RuleVariableForm(forms.ModelForm):
    class Meta:
        model = RuleVariable
        fields = '__all__'

    class Media:
        js = ('nhanes/js/rulevariable_dynamic.js',)


class RuleVariableAdmin(admin.ModelAdmin):
    form = RuleVariableForm
    list_display = ('rule', 'variable', 'dataset', 'is_source')

    class Media:
        js = ('nhanes/js/rulevariable_dynamic.js',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "dataset":
            kwargs["queryset"] = Dataset.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


class RuleVariableInline(admin.TabularInline):
    model = RuleVariable
    extra = 1
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
    list_display = ('rule', 'version', 'is_active', 'open_jupyter_link')
    search_fields = ('rule', 'description')
    list_filter = ('is_active', 'updated_at')
    inlines = [RuleVariableInline]
    actions = [setup_rules]

    # controler to ensure that Jupyter starts only once
    jupyter_started = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not RuleAdmin.jupyter_started:
            start_jupyter_notebook()
            RuleAdmin.jupyter_started = True

    def open_jupyter_link(self, obj):
        link = f"http://127.0.0.1:8888/edit/nhanes/normalizations/{obj.rule}/{obj.file_script}"
        return mark_safe(f'<a href="{link}" target="_blank">Edit in Jupyter</a>')

    open_jupyter_link.short_description = "Edit in Jupyter"


# ----------------------------------
# Work Process Rule Admin
# ----------------------------------

class WorkProcessRuleAdmin(admin.ModelAdmin):
    list_display = (
        'rule',
        'status',
        'last_synced_at',
        'execution_time',
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
        rules_to_run = Rule.objects.filter(id__in=selected_rules)
        normalization_manager = NormalizationManager(rules=rules_to_run)
        normalization_manager.apply_transformations()
        msg = f"Normalization applied for {rules_to_run.count()} selected rules."
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
admin.site.register(SystemConfig, SystemConfigAdmin)
admin.site.register(Data, DataAdmin)
# admin.site.register(QueryColumns, QueryColumnAdmin)
# admin.site.register(QueryStructure, QueryStructureAdmin)
# admin.site.register(QueryFilter, QueryFilterAdmin)
admin.site.register(Tag, TagAdmin)
# admin.site.register(NormalizedData, NormalizedDataAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleVariable, RuleVariableAdmin)
admin.site.register(WorkProcess, WorkProcessAdmin)
admin.site.register(WorkProcessMasterData, WorkProcessMasterDataAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(Version, VersionAdmin)


# class DatasetControlAdmin(admin.ModelAdmin):
#     list_display = (
#         "cycle_name",
#         "group_name",
#         "dataset_name",
#         "status",
#         "is_download",
#         "description",
#         "metadata_url_link",
#     )
#     list_filter = ("cycle", "status", "is_download", "dataset__group__group")
#     list_editable = (
#         "status",
#         "is_download",
#     )
#     search_fields = ("dataset__dataset", "cycle__cycle", "description")
#     raw_id_fields = ("dataset", "cycle")
#     # actions = [download_nhanes_files]

#     def dataset_name(self, obj):
#         return obj.dataset.dataset

#     def cycle_name(self, obj):
#         return obj.cycle.cycle

#     def group_name(self, obj):
#         return obj.dataset.group.group

#     # Shorting by related fields
#     dataset_name.admin_order_field = "dataset__dataset"
#     cycle_name.admin_order_field = "cycle__cycle"
#     group_name.admin_order_field = "dataset__group__group"

#     def get_queryset(self, request):
#         # Perform a prefetch_related to load the related group
#         queryset = super().get_queryset(request)
#         return queryset.select_related("dataset", "cycle", "dataset__group")

#     def metadata_url_link(self, obj):
#         if obj.metadata_url:
#             return format_html(
#                 "<a href='{url}' target='_blank'>{url}</a>", url=obj.metadata_url
#             )  # noqa: E501
#         else:
#             return "Dataset does not exist"

#     metadata_url_link.short_description = "no file"  # noqa: E501


# class SystemConfigAdmin(admin.ModelAdmin):
#     list_display = (
#         "config_key",
#         "config_value",
#     )
#     list_editable = ("config_value",)


# class DataAdmin(admin.ModelAdmin):
#     list_display = ("cycle", "group_name", "dataset", "field", "sample", "value")
#     list_filter = ("cycle", "dataset", "dataset__group__group")

#     def group_name(self, obj):
#         return obj.dataset.group.group

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related("dataset", "cycle", "dataset__group")
