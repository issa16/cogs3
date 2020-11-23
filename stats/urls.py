from . import views

from django.urls import path

urlpatterns = [
    path(
        'data-analytics/',
        views.StatsView.as_view(),
        name='data-analytics',
    ),
    path(
        'data-analytics/project-data/',
        views.ProjectDataView.as_view(),
        name='project-data',
    ),
    path(
        'data-analytics/compute-consumption-data/',
        views.ComputeConsumptionDataView.as_view(),
        name='compute-consumption-data',
    ),
    path(
        'data-analytics/storage-consumption-data/',
        views.StorageConsumptionDataView.as_view(),
        name='storage-consumption-data',
    ),
]
