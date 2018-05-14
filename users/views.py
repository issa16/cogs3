from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView

from users.forms import CustomUserCreationForm


class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def dispatch(self, *args, **kwargs):
        shib_username = self.request.session.get('shib', {}).get('username', None)
        if self.request.user.is_authenticated or shib_username is None:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
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
