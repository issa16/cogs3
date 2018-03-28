from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

from institution.models import Institution


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    user = instance

    # Determine the user's institution
    base_domain = user.username.split('@')[1]
    institution = Institution.objects.get(base_domain=base_domain)

    try:
        # Manually updating a user's profile via the admin screens.
        if user.profile:
            profile = user.profile
            profile.user = user
    except AttributeError:
        # Automated create or update when a user joins via shibboleth.
        profile, created = Profile.objects.update_or_create(
            user=user,
            institution=institution,
            defaults={
                'shibboleth_username': user.username,
            },
        )
    user.profile.save()
