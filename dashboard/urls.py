from . import views
from django.urls import path

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
]
