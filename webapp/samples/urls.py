from django.urls import path
from . import views

urlpatterns = [
    path('', views.CrudeSampleListView.as_view(), name='home'),
    path('sample/create/', views.CrudeSampleCreateView.as_view(), name='create_crude_sample'),
    path('sample/<pk>/update/', views.CrudeSampleUpdateView.as_view(), name='update_crude_sample'),
    path('sample/<pk>/delete/', views.CrudeSampleDeleteView.as_view(), name='delete_crude_sample'),
]
