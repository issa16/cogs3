from django.db import models
from django.utils.translation import gettext_lazy as _
from institution.models import Institution

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
        verbose_name_plural = _('Project Funding Sources')
        ordering = ('name', )


class FundingSource(models.Model):
    '''An individual funding source, such as a grant'''
    title = models.CharField(max_length=128)
    identifier = models.CharField(max_length=512)
    funding_body = models.ForeignKey(
        FundingBody,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('Funding Body'),
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = _('Project Funding Sources')
        ordering = ('created_time', )
