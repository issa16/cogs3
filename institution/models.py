from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    base_domain = models.CharField(max_length=255, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    identity_provider_login = models.URLField(max_length=200, blank=True)
    identity_provider_logout = models.URLField(max_length=200, blank=True)
    logo_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
