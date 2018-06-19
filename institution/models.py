from django.db import models
from django.utils.translation import gettext as _

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
        return _(self.name)

    def id_str(self):
        return self.name.lower().replace(" ", "-")

    class Meta:
        ordering = ('name', )

    @property
    def is_cardiff(self):
        return self.base_domain == 'cardiff.ac.uk'

    @property
    def is_swansea(self):
        return self.base_domain == 'swansea.ac.uk'

    @property
    def is_bangor(self):
        return self.base_domain == 'bangor.ac.uk'

    @property
    def is_aber(self):
        return self.base_domain == 'aber.ac.uk'

    @property
    def is_sunbird(self):
        return self.is_swansea or self.is_aber

    @property
    def is_hawk(self):
        return self.is_cardiff or self.is_bangor
