from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from institution.exceptions import (InvalidInstitutionalEmailAddress,
                                    InvalidInstitutionalIndentityProvider)


class Institution(models.Model):

    class Meta:
        ordering = ('name', )

    name = models.CharField(max_length=255, unique=True)
    base_domain = models.CharField(max_length=255, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    identity_provider = models.URLField(
        max_length=200,
        blank=True,
        verbose_name='Shibboleth Identity Provider',
    )
    support_email = models.EmailField(blank=True)
    logo_path = models.CharField(max_length=255, blank=True)

    @classmethod
    def parse_support_email_from_user_email(cls, email):
        """
        Parse the institutions support email address from a user's email address.

        Args:
            email (str): User's email address.
        """
        try:
            _, domain = email.split('@')
            support_email = Institution.objects.get(base_domain=domain).support_email
            return support_email if support_email else settings.DEFAULT_SUPPORT_EMAIL
        except Exception:
            return settings.DEFAULT_SUPPORT_EMAIL
        
    @classmethod
    def is_valid_email_address(cls, email):
        """
        Ensure the email address is a valid institutional email address.

        Args:
            email (str): An email address to validate.
        """
        try:
            _, domain = email.split('@')
            Institution.objects.get(base_domain=domain)
        except Exception:
            raise InvalidInstitutionalEmailAddress('Email address domain is not supported.')
        else:
            return True

    @classmethod
    def is_valid_identity_provider(cls, identity_provider):
        """
        Ensure the identity provider is a valid institutional identity provider.

        Args:
            identity_provider (str): An identity provider to validate.
        """
        try:
            Institution.objects.get(identity_provider=identity_provider)
        except Exception:
            raise InvalidInstitutionalIndentityProvider('Identity provider is not supported.')
        else:
            return True

    def id_str(self):
        return self.name.lower().replace(" ", "-")

    @property
    def is_cardiff(self):
        return self.base_domain == 'cardiff.ac.uk'

    @property
    def is_swan(self):
        return self.base_domain == 'swan.ac.uk'

    @property
    def is_bangor(self):
        return self.base_domain == 'bangor.ac.uk'

    @property
    def is_aber(self):
        return self.base_domain == 'aber.ac.uk'

    @property
    def is_sunbird(self):
        return self.is_swan or self.is_aber

    @property
    def is_hawk(self):
        return self.is_cardiff or self.is_bangor

    def __str__(self):
        return _(self.name)
