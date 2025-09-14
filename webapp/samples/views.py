from django.views import generic
from django.urls import reverse_lazy
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
