from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from .forms import CustomUserCreationForm
from users.models import Profile


class LogoutView(TemplateView):

    def get(self, *args, **kwargs):
        # Logout the user from the application and redirect them to the shibboleth logout url.
        if self.request.user.is_authenticated:
            user = self.request.user
            profile = Profile.objects.get(user=user)
            url = profile.institution.identity_provider_logout
            logout(self.request)
            try:
                del self.request.session['shib']
            except KeyError:
                pass
            return redirect(url)


class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def dispatch(self, *args, **kwargs):
        shib_username = self.request.session.get('shib', {}).get('username', None)
        if self.request.user.is_authenticated or shib_username is None:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)
