from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q
from .models import CrudeSample, Subject
from .forms import CrudeSampleForm

class CrudeSampleListView(generic.ListView):
    model = CrudeSample
    context_object_name = 'crudesample_list'
    template_name = 'samples/crudesample_list.html'

class CrudeSampleCreateView(generic.CreateView):
    model = CrudeSample
    form_class = CrudeSampleForm
    template_name = 'samples/crudesample_form.html'
    success_url = reverse_lazy('home')

class CrudeSampleUpdateView(generic.UpdateView):
    model = CrudeSample
    form_class = CrudeSampleForm
    template_name = 'samples/crudesample_form.html'
    success_url = reverse_lazy('home')

class CrudeSampleDeleteView(generic.DeleteView):
    model = CrudeSample
    template_name = 'samples/crudesample_confirm_delete.html'
    success_url = reverse_lazy('home')

class SearchResultsView(generic.ListView):
    model = CrudeSample
    context_object_name = 'crudesample_list'
    template_name = 'samples/crudesample_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return CrudeSample.objects.filter(
                Q(barcode__icontains=query) |
                Q(subject__subject_id__icontains=query) |
                Q(project_name__icontains=query) |
                Q(sequence_filename__icontains=query)
            )
        return CrudeSample.objects.none()
