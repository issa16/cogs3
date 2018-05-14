from django.db import models

from institution.exceptions import InvalidIndentityProvider
from institution.exceptions import InvalidInstitution


class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    base_domain = models.CharField(max_length=255, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    identity_provider = models.URLField(max_length=200, blank=True)
    logo_path = models.CharField(max_length=255, blank=True)

    @classmethod
    def is_valid_email_address(cls, email):
        try:
            _, domain = email.split('@')
            Institution.objects.get(base_domain=domain)
        except Exception:
            raise InvalidInstitution('Email address domain is not supported.')
        else:
            return True

    @classmethod
    def is_valid_identity_provider(cls, identity_provider):
        try:
            Institution.objects.get(identity_provider=identity_provider)
        except Exception:
            raise InvalidIndentityProvider('Identity provider is not supported.')
        else:
            return True

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )
