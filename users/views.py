from django.conf import settings
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from common.util import mailing_list_subscribe
from users.forms import RegisterForm
from users.forms import TermsOfServiceForm
from users.models import CustomUser
from institution.models import Institution

class MailingListMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.session.shib.username:
            _, domain = request.session.shib.username.split('@')
            self.institution = Institution.objects.get(base_domain=domain)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_list'] = None
        context['institution_name'] = None
        if self.institution:
            context['mailing_list'] = self.institution.local_mailing_list_name
            context['institution_name'] = _(self.institution.name)

        return context

    def form_valid(self, form):
        if self.institution and form.instance.join_mailing_list:
            mailing_list_subscribe(
                self.institution.local_mailing_list_link,
                form.instance.email
            )
        return super().form_valid(form)


class TermsOfService(LoginRequiredMixin, generic.UpdateView):
    form_class = TermsOfServiceForm
    model = CustomUser
    success_url = reverse_lazy('home')
    template_name = 'terms_of_service/index.html'

    def get_object(self, queryset=None):
        return self.request.user


class CompleteRegistrationView(LoginRequiredMixin, MailingListMixin,
                               generic.UpdateView):
    form_class = RegisterForm
    model = CustomUser
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, *args, **kwargs):
        if not self.request.session.get('shib', None):
            return redirect(reverse('login'))
        if (self.request.user.is_authenticated
            and self.request.user.first_name != ''
            and self.request.user.last_name != ''):
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)


class RegisterView(MailingListMixin, generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def dispatch(self, *args, **kwargs):
        if not self.request.session.get('shib', None):
            return redirect(reverse('login'))
        if self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.is_active = True
        form.instance.is_shibboleth_login_required = True
        form.instance.email = self.request.session['shib']['username']
        form.instance.username = form.instance.email
        form.instance.set_password(CustomUser.objects.make_random_password(length=30))
        return super().form_valid(form)


class LogoutView(generic.TemplateView):

    def get(self, *args, **kwargs):
        # If the user has logged in via a shibboleth identity provider, then they must
        # reauthenticate with the identity provider after logging out of the django application.
        if self.request.user.is_shibboleth_login_required:
            self.request.session[settings.SHIBBOLETH_FORCE_REAUTH_SESSION_KEY] = True
            self.request.session.set_expiry(0)
        auth.logout(self.request)
        return redirect(reverse('logged_out'))
