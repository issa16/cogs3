from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView

from .forms import CustomUserCreationForm


class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def dispatch(self, *args, **kwargs):
        shib_username = self.request.session.get('shib', {}).get('username', None)
        if self.request.user.is_authenticated or shib_username is None:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)


class LogoutView(TemplateView):

    def get(self, *args, **kwargs):
        # Logout the user.
        auth.logout(self.request)
        # Force the user to reauthenticate with shibboleth, they must close their browser.
        self.request.session[settings.SHIBBOLETH_FORCE_REAUTH_SESSION_KEY] = True
        self.request.session.set_expiry(0)
        return redirect(reverse('logged_out'))
