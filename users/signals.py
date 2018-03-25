from django.conf import settings
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

    # Update the user's profile
    profile, created = Profile.objects.get_or_create(user=user, institution=institution)
    profile.shibboleth_username = user.username
    profile.save()
