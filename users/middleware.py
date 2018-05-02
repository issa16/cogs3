from django.conf import settings
from django.contrib import auth
from django.contrib.auth import load_backend
from django.contrib.auth.backends import RemoteUserBackend
from django.http import HttpResponseRedirect
from django.urls import resolve
from django.urls import reverse

from shibboleth.middleware import ShibbolethRemoteUserMiddleware
from shibboleth.middleware import ShibbolethValidationError


class SCWRemoteUserMiddleware(ShibbolethRemoteUserMiddleware):

    def process_request(self, request):
        # The identity of external collaborators is managed within the django application.
        # Therefore, exclude the external collaborator login form from the SCW Remote User
        # Middleware.
        if request.path.startswith(reverse('external-login')):
            return

        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the authentication middleware to "
                " be installed. Edit your MIDDLEWARE setting to insert "
                "'django.contrib.auth.middleware.AuthenticationMiddleware' "
                "before the RemoteUserMiddleware class.")

        # Prevent the user from logging in if the application requires the user to
        # reauthenticate with their shibboleth identity provider.
        # This will require the user to close their browser
        if request.session.get(settings.SHIBBOLETH_FORCE_REAUTH_SESSION_KEY) == True:
            return

        # Check the remote user header.
        username = request.META.get(self.header, None)

        # Check the 'shib' session variable.
        if not username:
            username = request.session.get('shib', {}).get('username', None)

        # If specified header or session variable doesn't exist then return
        # (leaving request.user set to AnonymousUser by the AuthenticationMiddleware).
        if not username:
            if self.force_logout_if_no_header and request.user.is_authenticated:
                self._remove_invalid_user(request)
            return

        # If the user is already authenticated and that user is the user we are getting passed in
        # the headers, then the correct user is already persisted in the session and we don't need
        # to continue.
        if request.user.is_authenticated:
            if request.user.username == self.clean_username(username, request):
                return
            else:
                self._remove_invalid_user(request)

        # Make sure we have all required Shibboleth elements before proceeding.
        shib_meta, error = ShibbolethRemoteUserMiddleware.parse_attributes(request)

        # Add parsed attributes to the session.
        request.session['shib'] = shib_meta

        if error:
            raise ShibbolethValidationError('All required Shibboleth elements not found. %s' % shib_meta)

        # We are seeing this user for the first time in this session, attempt to authenticate
        # the user.
        user = auth.authenticate(remote_user=username, shib_meta=shib_meta)

        if user:
            # User is valid. Set request.user and persist user in the session by logging the
            # user in.
            request.user = user
            auth.login(request, user)
        else:
            # Redirect the user to apply for an account
            url_name = resolve(request.path_info).url_name
            if url_name != 'register':
                return HttpResponseRedirect(reverse('register'))

    @classmethod
    def _remove_invalid_user(cls, request):
        """
        Remove the current authenticated user in the request which is invalid but only if the
        user is authenticated via the RemoteUserBackend.
        """
        try:
            stored_backend = load_backend(request.session.get(auth.BACKEND_SESSION_KEY, ''))
        except ImportError:
            # Backend failed to load
            auth.logout(request)
        else:
            if isinstance(stored_backend, RemoteUserBackend):
                auth.logout(request)
