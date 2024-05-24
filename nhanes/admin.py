from django.contrib import admin
from django.utils.html import format_html
# from django.contrib import messages
from .models import DatasetControl, Cycle, Dataset, Field, FieldCycle, Data, Group, SystemConfig, QueryColumns, QueryStructure, QueryFilter  # noqa: E501
from nhanes.services.consult import download_query_results
# TODO: Add the download_nhanes_files function to the imports
# from nhanes.services.loader import download_nhanes_files
import json


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'dataset', 'description')
    list_filter = ('group__group', )
    search_fields = ('dataset', 'description', 'group__group')

    def get_queryset(self, request):
        # This function serves to optimize the loading of queries
        queryset = super().get_queryset(request)
        return queryset.select_related('group')

    def group_name(self, obj):
        return obj.group.group


class DatasetControlAdmin(admin.ModelAdmin):
    list_display = (
        'cycle_name',
        'group_name',
        
        'dataset_name',
        'status',
        'is_download',
        'description',
        'metadata_url_link'
        )
    list_filter = ('cycle', 'status', 'is_download', 'dataset__group__group')
    list_editable = ('status', 'is_download',)
    search_fields = ('dataset__dataset', 'cycle__cycle', 'description')
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

    def metadata_url_link(self, obj):
        if obj.metadata_url:
            return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.metadata_url)  # noqa: E501
        else:
            return "Nenhuma URL"
    metadata_url_link.short_description = 'Metadata URL'  # noqa: E501


class FieldCycleAdmin(admin.ModelAdmin):
    list_display = (
        'cycle',
        'variable_name',
        'sas_label',
        'type',
        'english_text',
        'formatted_value_table',
        )

    def formatted_value_table(self, obj):
        # Assume that obj.value_table is the JSON field
        try:
            data = json.loads(obj.value_table)
            html = '<table border="1">'
            html += '<tr><th>Code or Value</th><th>Value Description</th><th>Count</th><th>Cumulative</th><th>Skip to Item</th></tr>'  # noqa: E501
            for item in data:
                html += f"<tr><td>{item.get('Code or Value')}</td><td>{item.get('Value Description')}</td><td>{item.get('Count')}</td><td>{item.get('Cumulative')}</td><td>{item.get('Skip to Item')}</td></tr>"  # noqa: E501
            html += '</table>'
            return format_html(html)
        except json.JSONDecodeError:
            return "Invalid JSON"

    formatted_value_table.short_description = 'Value Table'

    search_fields = (
        'variable_name',
        'sas_label',
        'english_text',
        'value_table'
        )


class CycleAdmin(admin.ModelAdmin):
    list_display = (
        'cycle',
        'year_code',
        'base_dir',
        'dataset_url_pattern'
        )


class SystemConfigAdmin(admin.ModelAdmin):
    list_display = (
        'config_key',
        'config_value',
        )
    list_editable = ('config_value', )


class DataAdmin(admin.ModelAdmin):
    list_display = (
        'cycle',
        'group_name',
        'dataset',
        'field',
        'sample',
        'value'
        )
    list_filter = ('cycle', 'dataset', 'dataset__group__group')

    def group_name(self, obj):
        return obj.dataset.group.group

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('dataset', 'cycle', 'dataset__group')


class FieldAdmin(admin.ModelAdmin):
    list_display = (
        'field',
        'internal_id',
        'description',
        )
    list_editable = ('internal_id',)
    search_fields = ('field', 'internal_id', 'description',)


class QueryColumnAdmin(admin.ModelAdmin):
    list_display = ('column_name', 'internal_data_key', 'column_description')
    search_fields = ('column_name', 'column_description')


class QueryFilterInline(admin.TabularInline):
    model = QueryFilter
    extra = 0  # Define number of extra forms to display


class QueryStructureAdmin(admin.ModelAdmin):
    list_display = ('structure_name', 'no_conflict', 'no_multi_index')
    list_editable = ('no_conflict', 'no_multi_index',)
    search_fields = ('structure_name',)
    # Easy access to the filters
    filter_horizontal = ('columns',)
    # Add filters to the QueryStructure page
    inlines = [QueryFilterInline]
    # Add actions to the QueryStructure page
    actions = [download_query_results]


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DatasetControl, DatasetControlAdmin)
admin.site.register(FieldCycle, FieldCycleAdmin)
admin.site.register(Cycle, CycleAdmin)
admin.site.register(SystemConfig, SystemConfigAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(QueryColumns, QueryColumnAdmin)
admin.site.register(QueryStructure, QueryStructureAdmin)

admin.site.register(QueryFilter)
admin.site.register(Group)
