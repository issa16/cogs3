"""cogs3 URL Configuration"""
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('projects/', include('project.urls')),
    path('admin/', admin.site.urls),
]
