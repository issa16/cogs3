import re

from django.conf import settings
from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import generic
from django.views.generic import TemplateView

from openldap.api import user_api
from users.forms import CustomUserCreationForm


class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.is_active = True
        form.instance.is_shibboleth_login_required = True
        return super().form_valid(form)


class LogoutView(TemplateView):

    def get(self, *args, **kwargs):
        # If the user has logged in via a shibboleth identity provider, then they must
        # reauthenticate with the identity provider after logging out of the django application.
        if self.request.user.is_shibboleth_login_required:
            self.request.session[settings.SHIBBOLETH_FORCE_REAUTH_SESSION_KEY] = True
            self.request.session.set_expiry(0)

        auth.logout(self.request)

        return redirect(reverse('logged_out'))


def reset_scw_password(request):
    """
    Reset a user's SCW account password.

    Args:
        request (django.http.request.HttpRequest): Django HTTP request - required
    """
    try:
        # Ensure password fields match.
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        if password != password_confirm:
            raise ValidationError()

        # Ensure password complies with OpenLDAP password policy.
        pattern = re.compile("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}")
        if not pattern.match(password):
            raise ValidationError()

        # Submit an OpenLDAP password reset request.
        user_api.reset_user_password.delay(user=request.user, password=password)

        message = _('Successfully submitted a password reset request. You should receive a '
                    'confirmation email once the request has been processed.')
        return JsonResponse(
            status=200,
            data={'data': message},
        )
    except Exception as e:
        return JsonResponse(status=400)
