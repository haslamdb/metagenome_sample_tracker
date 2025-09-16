from django.contrib import admin
from .models import AnalysisID
from .id_generator import create_analysis_id

@admin.action(description='Generate Analysis ID(s) for selected samples')
def generate_analysis_ids_action(modeladmin, request, queryset):
    count = 0
    for obj in queryset:
        # Ensure an ID doesn't already exist
        if not AnalysisID.objects.filter(object_id=obj.id, content_type__model=obj.__class__.__name__.lower()).exists():
            new_id = create_analysis_id(obj)
            if new_id:
                count += 1
    modeladmin.message_user(request, f'{count} new Analysis ID(s) were generated.')

@admin.register(AnalysisID)
class AnalysisIDAdmin(admin.ModelAdmin):
    list_display = ('analysis_id', 'content_object', 'created_at')
    search_fields = ('analysis_id',)
    list_filter = ('content_type', 'created_at')