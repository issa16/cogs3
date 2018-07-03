from django.conf import settings
from django.contrib.auth.signals import user_logged_in


def login_user(sender, user, request, **kwargs):
    if user.is_shibboleth_login_required:
        # Reauthentication via shibboleth is not required until a user logs out.
        request.session[settings.SHIBBOLETH_FORCE_REAUTH_SESSION_KEY] = False


user_logged_in.connect(login_user)
