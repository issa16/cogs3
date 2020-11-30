from . import views

from django.urls import path

urlpatterns = [
    path(
        'data-analytics/',
        views.StatsView.as_view(),
        name='data-analytics',
    ),
]
