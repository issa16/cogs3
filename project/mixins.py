from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect
from django.urls import reverse


class PermissionAndLoginRequiredMixin(PermissionRequiredMixin):
    """
    CBV mixin which extends the PermissionRequiredMixin to verify
    that the user is logged in and performs a separate action if not
    """

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('home'))

    def handle_not_logged_in(self):
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_not_logged_in()
        return super(PermissionAndLoginRequiredMixin, self).dispatch(
            request,
            *args,
            **kwargs,
        )
