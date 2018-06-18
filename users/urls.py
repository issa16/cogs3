from . import views

from django.urls import path

urlpatterns = [
    path(
        'update/',
        views.UpdateView.as_view(),
        name='update-user',
    ),
]
