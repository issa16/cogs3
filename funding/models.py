from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser

# Create your models here.


class FundingBody(models.Model):
    '''Represent organisations that fund research projects
       through funding sources such as grants '''
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    description = models.CharField(max_length=512)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('Funding Bodies')
        ordering = ('name', )


class Attribution(models.Model):
    ''' An attribution that can be added to a project '''
    title = models.CharField(max_length=128)
    identifier = models.CharField(max_length=512)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_by',
        on_delete=models.CASCADE,
        verbose_name=_('Created By'),
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class FundingSource(Attribution):
    '''An individual funding source, such as a grant'''
    funding_body = models.ForeignKey(
        FundingBody,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('Funding Body'),
    )
    pi_email = models.CharField(
        max_length=128,
        null=True,
        verbose_name=_('PI Email'),
    )
    pi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='pi',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('PI'),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = _('Funding Sources')
        ordering = ('created_time', )

    def save(self, *args, **kwargs):
        if getattr(self, 'pi_email_changed', True):
            matching_users = CustomUser.objects.filter(email=self.pi_email)
            if matching_users.exists():
                self.pi = matching_users.get()
                self.pi_email = None
            elif self.pi:
                self.pi = None

        super().save(*args, **kwargs)
