from django import forms
from .models import CrudeSample

class CrudeSampleForm(forms.ModelForm):
    class Meta:
        model = CrudeSample
        fields = ['barcode', 'subject', 'collection_date', 'sample_source', 'notes', 'status', 'project_name']
        widgets = {
            'collection_date': forms.DateInput(attrs={'type': 'date'}),
        }
