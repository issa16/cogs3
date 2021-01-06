from django.urls import path

from . import views

urlpatterns = [
    # -------------------------------------------------------------------------
    # Paths for the data-analytics dashboard
    # -------------------------------------------------------------------------
    path(
        'data-analytics/',
        views.LatestProjectView.as_view(),
        name='data-analytics',
    ),
    path(
        'data-analytics/search/',
        views.ProjectSearchView.as_view(),
        name='data-analytics-search',
    ),
    path(
        'data-analytics/search/json/',
        views.ProjectStatsParserJSONView,
        name='data-analytics-search-json',
    ),
    path(
        'data-analytics/<str:code>/',
        views.ProjectDetailView.as_view(),
        name='data-analytics-detail',
    ),
]
