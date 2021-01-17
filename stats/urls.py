from django.urls import path

from . import views

urlpatterns = [
    path(
        'data-analytics/',
        views.IndexView.as_view(),
        name='data-analytics',
    ),
    path(
        'data-analytics/project/json/',
        views.ProjectStatsParserJSONView,
        name='data-analytics-project-json',
    ),
    path(
        'data-analytics/user/json/',
        views.UserStatsParserJSONView,
        name='data-analytics-user-json',
    ),
]
