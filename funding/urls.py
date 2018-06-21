from . import views

from django.urls import path

urlpatterns = [
    path(
        'create/',
        views.FundingSourceCreateView.as_view(),
        name='create-funding-source',
    ),
    path(
        'list/',
        views.FundingSourceListView.as_view(),
        name='list-funding-sources',
    ),
    path(
        '<int:pk>/update/',
        views.FundingSourceUpdateView.as_view(),
        name='funding-source-update',
    ),
    path(
        '<int:pk>/delete/',
        views.FundingSourceDeleteView.as_view(),
        name='delete-funding-source',
    ),
]
