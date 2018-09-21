from django.conf import settings
from django.db import models
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from simple_history.models import HistoricalRecords

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

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('Funding Bodies')
        ordering = ('name', )


class AttributionManager(models.Manager):
    def get_fundingsources(self):
        return [attribution
                for attribution in self.all()
                if attribution.is_fundingsource]

    def get_publications(self):
        return [attribution
                for attribution in self.all()
                if attribution.is_publication]


class Attribution(models.Model):
    ''' An attribution that can be added to a project '''
    objects = AttributionManager()

    title = models.CharField(max_length=128)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_by',
        on_delete=models.CASCADE,
        verbose_name=_('Created By'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owner',
        on_delete=models.CASCADE,
        verbose_name=_('Owner'),
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    @property
    def is_fundingsource(self):
        try:
            self.fundingsource
            return True
        except self._meta.model.fundingsource.RelatedObjectDoesNotExist:
            return False

    @property
    def is_publication(self):
        try:
            self.publication
            return True
        except self._meta.model.publication.RelatedObjectDoesNotExist:
            return False

    @property
    def type(self):
        if self.is_fundingsource:
            return 'fundingsource'
        else:
            return 'publication'

    @property
    def verbose_type(self):
        if self.is_fundingsource:
            return 'Funding Source'
        else:
            return 'Publication'

    @property
    def child(self):
        try:
            child = self.fundingsource
            return child
        except self._meta.model.fundingsource.RelatedObjectDoesNotExist:
            return self.publication

    history = HistoricalRecords()

    def string(self, user=False):
        try:
            return self.fundingsource.string(user)
        except self._meta.model.fundingsource.RelatedObjectDoesNotExist:
            return self.title

    class Meta:
        verbose_name_plural = _('Attributions')
        ordering = ('created_time', )


class FundingSource(Attribution):
    '''An individual funding source, such as a grant'''

    # AMS number
    identifier = models.CharField(
        max_length=128,
        null=True,
        verbose_name=_('Local Institutional Identifier'),
    )
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
    amount = models.PositiveIntegerField(
        verbose_name=_('Grant attributable to Supercomputing Wales (in £)'),
    )
    approved = models.BooleanField(
        default=False,
        verbose_name=_('Atributed to SCW by the PI'),
    )

    users = models.ManyToManyField(
        CustomUser,
        blank=True,
        through='FundingSourceMembership',
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def string(self, user=False):
        if user is not False:
            if self.approved:
                if FundingSourceMembership.objects.filter(
                    fundingsource=self,
                    user=user,
                    approved=True
                ).exists():
                    return self.title
            return self.title + ' (awaiting approval)'
        return self.title

    class Meta:
        verbose_name_plural = _('Funding Sources')
        ordering = ('created_time', )

    def save(self, *args, **kwargs):
        new_pi = False
        matching = self.__class__._default_manager.filter(id=self.id)
        if matching.exists():
            old = self.__class__._default_manager.get(id=self.id)
            new_pi = self.pi_email != old.pi_email
        else:
            new_pi = True

        if new_pi:
            # Get the PI or create if not found
            matching_users = CustomUser.objects.filter(email=self.pi_email)
            if matching_users.exists():
                self.pi = matching_users.get()
            else:
                self.pi = CustomUser.objects.create_pending_shibbolethuser(
                    email=self.pi_email,
                    password=CustomUser.objects.make_random_password(length=30)
                )
            # Make sure the PI is in the pi group
            pi_group = Group.objects.get(name='funding_source_pi')
            pi_group.user_set.add(self.pi)

        if self.pi.profile.institution.needs_funding_approval:
            self.owner = self.pi
        else:
            self.owner = self.created_by

        self.pi_email = None

        super().save(*args, **kwargs)

        # Automatically add the user who created the funding source to users
        FundingSourceMembership.objects.get_or_create(
            user=self.created_by,
            fundingsource=self,
            defaults=dict(
                approved=False,
            )
        )

        # When a funding source is approved, the PI and the creator are automatically approved as members
        if matching.exists():
            if self.approved:
                if self.approved != old.approved:
                    creatormembership = FundingSourceMembership.objects.get(
                        user=self.created_by,
                        fundingsource=self,
                    )
                    creatormembership.approved = True
                    creatormembership.save()

                if self.pi.profile.institution.needs_funding_approval:
                    FundingSourceMembership.objects.get_or_create(
                        user=self.pi,
                        fundingsource=self,
                        defaults=dict(
                            approved=True,
                        )
                    )


class FundingSourceMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fundingsource = models.ForeignKey(FundingSource, on_delete=models.CASCADE)

    approved = models.BooleanField(
        default=False,
        verbose_name=_('Approved by PI'),
    )

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "fundingsource"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Prevent the admin interface from creating a duplicate
        extras = self.__class__._default_manager.filter(
            user=self.user,
            fundingsource=self.fundingsource,
        )[1:]
        self.__class__._default_manager.filter(pk__in=extras).delete()


class Publication(Attribution):
    '''An individual funding source, such as a grant'''
    # Cronfa URL for Swansea
    url_validator = URLValidator(schemes=['http', 'https'])
    url = models.CharField(
        max_length=128,
        null=True,
        validators=[url_validator],
        verbose_name=_('URL of the publication'),
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = _('Publications')
        ordering = ('created_time', )

    def save(self, *args, **kwargs):
        self.owner = self.created_by
        super().save( *args, **kwargs )


