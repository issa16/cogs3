from stats.views import StatsView
from django.urls import path

urlpatterns = [
    path(
        'data-analytics/',
        StatsView.as_view(),
        name='data-analytics',
    ),
]
