"""cogs3 URL Configuration"""
from django.contrib import admin
from django.contrib import auth
from django.urls import include
from django.urls import path
from django.views.generic.base import TemplateView

from institution.models import Institution
from users.views import RegisterView

urlpatterns = [
    path(
        'shib/',
        include('shibboleth.urls', namespace='shibboleth'),
    ),
    path(
        '',
        include('dashboard.urls'),
    ),
    path(
        'accounts/login/',
        auth.views.LoginView.as_view(
            redirect_authenticated_user=True,
            extra_context={'institutions': Institution.objects.all()},
        ),
        name='login',
    ),
    path(
        'accounts/',
        include('django.contrib.auth.urls'),
    ),
    path(
        'accounts/register/',
        RegisterView.as_view(),
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
