"""cogs3 URL Configuration"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include
from django.urls import path
from django.views.generic.base import TemplateView

from institution.models import Institution
from users.openldap import reset_openldap_password
from users.views import LogoutView
from users.views import RegisterView
from users.views import TermsOfService

# Admin config
admin.site.site_header = 'Cogs3 Administration'
admin.site.index_title = 'Cogs3'
admin.site.site_title = 'Administration'

urlpatterns = i18n_patterns(
    path(
        'queue/',
        include('django_rq.urls'),
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
                'institutions': Institution.objects.order_by('name'),
                'shibboleth_idp_login': settings.SHIBBOLETH_IDENTITY_PROVIDER_LOGIN,
            },
            template_name="registration/educational_login.html",
        ),
        name='login',
    ),
    path(
        'accounts/external/login/',
        LoginView.as_view(
            redirect_authenticated_user=True,
            template_name="registration/external_login.html",
        ),
        name='external-login',
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
        'accounts/scw/password-reset/',
        reset_openldap_password,
        name='scw-password-reset',
    ),
    path(
        'projects/',
        include('project.urls'),
    ),
    path(
        'admin/',
        admin.site.urls,
    ),
    path(
        'terms-and-conditions/',
        TermsOfService.as_view(),
        name='terms-of-service',
    ),
    path(
        '',
        include('stats.urls'),
    ),
)
