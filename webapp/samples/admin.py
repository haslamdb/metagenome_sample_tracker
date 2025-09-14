from django.contrib import admin
from .models import Subject, CrudeSample

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id',)
    search_fields = ('subject_id',)

@admin.register(CrudeSample)
class CrudeSampleAdmin(admin.ModelAdmin):
    list_display = (
        'barcode',
        'subject',
        'collection_date',
        'sample_source',
        'status',
        'project_name',
        'sequence_filename'
    )
    list_filter = ('sample_source', 'status', 'project_name', 'collection_date')
    search_fields = ('barcode', 'subject__subject_id', 'sequence_filename')
    ordering = ('-collection_date',)
