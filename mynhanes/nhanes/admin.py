import json
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Cycle,
    Group,
    Dataset,
    Variable,
    VariableCycle,
    DatasetCycle,
    SystemConfig,
    RawData,
    QueryColumns,
    QueryStructure,
    QueryFilter,
    Field,
    Tag,
    NormalizedData,
    NormalizationRule,
    WorkProcess,
    WorkProcessMasterData,
    Logs,
)
from nhanes.services import query
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.management import call_command
from django.contrib import messages


# from .services import query


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
    )
    search_fields = ("variable", "description")


class VariableCycleAdmin(admin.ModelAdmin):
    list_display = (
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


class RawDataAdmin(admin.ModelAdmin):
    model = RawData


class FieldAdmin(admin.ModelAdmin):
    model = Field


class TagAdmin(admin.ModelAdmin):
    model = Tag


# class NormalizedDataAdmin(admin.ModelAdmin):
#     model = NormalizedData
@admin.register(NormalizedData)
class NormalizedDataAdmin(admin.ModelAdmin):
    list_display = ('cycle', 'dataset', 'field', 'sample', 'sequence', 'value')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reset-normalizationdata/', self.reset_normalizationdata),
        ]
        return custom_urls + urls

    def reset_normalizationdata(self, request):
        try:
            call_command('reset_normalizationdata')
            self.message_user(request, 'All data and auto-increment ID for NormalizedData have been reset.', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f'Error: {str(e)}', messages.ERROR)
        return HttpResponseRedirect("../")


class NormalizationRuleAdmin(admin.ModelAdmin):
    model = NormalizationRule


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


class QueryColumnAdmin(admin.ModelAdmin):
    list_display = ("column_name", "internal_data_key", "column_description")
    search_fields = ("column_name", "column_description")


class QueryFilterInline(admin.TabularInline):
    model = QueryFilter
    extra = 0  # Define number of extra forms to display


class QueryStructureAdmin(admin.ModelAdmin):
    list_display = ("structure_name", "no_conflict", "no_multi_index")
    list_editable = (
        "no_conflict",
        "no_multi_index",
    )
    search_fields = ("structure_name",)
    # Easy access to the filters
    filter_horizontal = ("columns",)
    # Add filters to the QueryStructure page
    inlines = [QueryFilterInline]
    # Add actions to the QueryStructure page
    # actions = [download_query_results]
    actions = [query.download_data_report]


admin.site.register(Cycle, CycleAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Variable, VariableAdmin)
admin.site.register(VariableCycle, VariableCycleAdmin)
admin.site.register(DatasetCycle, DatasetCycleAdmin)
admin.site.register(SystemConfig, SystemConfigAdmin)
admin.site.register(RawData, RawDataAdmin)
admin.site.register(QueryColumns, QueryColumnAdmin)
admin.site.register(QueryStructure, QueryStructureAdmin)
# admin.site.register(QueryFilter, QueryFilterAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Tag, TagAdmin)
# admin.site.register(NormalizedData, NormalizedDataAdmin)
admin.site.register(NormalizationRule, NormalizationRuleAdmin)
admin.site.register(WorkProcess, WorkProcessAdmin)
admin.site.register(WorkProcessMasterData, WorkProcessMasterDataAdmin)
admin.site.register(Logs, LogsAdmin)


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



