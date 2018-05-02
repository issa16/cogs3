from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from institution.models import Institution
from users.models import Profile
from users.models import ShibbolethProfile


def login_user(sender, user, request, **kwargs):
    if user.is_shibboleth_login_required:
        # Reauthentication via shibboleth is not required until a user logs out.
        request.session[settings.SHIBBOLETH_FORCE_REAUTH_SESSION_KEY] = False


user_logged_in.connect(login_user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    user = instance
    if user.is_shibboleth_login_required:
        username, domain = user.email.split('@')
        institution = Institution.objects.get(base_domain=domain)
        ShibbolethProfile.objects.update_or_create(
            user=user,
            defaults={
                'shibboleth_id': username,
                'institution': institution,
            },
        )
    else:
        Profile.objects.update_or_create(user=user)
    user.profile.save()
