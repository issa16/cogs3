"""cogs3 URL Configuration"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic.base import TemplateView
from users.views import Register

urlpatterns = [
    path(
        '',
        include('dashboard.urls'),
    ),
    path(
        'accounts/',
        include('django.contrib.auth.urls'),
    ),
    path(
        'accounts/register/',
        Register.as_view(),
        name='register',
    ),
    path(
        'projects/',
        include('project.urls'),
    ),
    path(
        'admin/',
        admin.site.urls,
    ),
]
