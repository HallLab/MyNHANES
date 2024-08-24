from django.urls import path
from nhanes import views

urlpatterns = [
    # outras URLs
    path(
        'get-datasets/',
        views.get_datasets_for_variable,
        name='get_datasets_for_variable'
        ),
    # path('get_datasets/', views.get_datasets, name='get_datasets'),
    ]
