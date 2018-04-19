"""cogs3 URL Configuration"""
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include
from django.urls import path
from django.views.generic.base import TemplateView

from institution.models import Institution
from users.views import LogoutView
from users.views import RegisterView

urlpatterns = [
    path(
        'queue/',
        include('django_rq.urls'),
    ),
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
        LoginView.as_view(
            redirect_authenticated_user=True,
            extra_context={
                'institutions': Institution.objects.all(),
            },
        ),
        name='login',
    ),
    path(
        'accounts/logout/',
        LogoutView.as_view(),
        name='logout',
    ),
    path(
        'accounts/logged_out/',
        TemplateView.as_view(template_name="registration/logged_out.html"),
        name='logged_out',
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
