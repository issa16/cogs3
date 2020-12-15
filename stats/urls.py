from django.urls import path

from . import views

urlpatterns = [
    path(
        'data-analytics/',
        views.StatsView.as_view(),
        name='data-analytics',
    ),
]
