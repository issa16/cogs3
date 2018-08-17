from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from institution.models import Institution


class Profile(models.Model):

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    scw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('SCW username'),
    )
    hpcw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('HPCW username'),
    )
    hpcw_email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name=_('HPCW email address'),
    )
    raven_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Raven username'),
    )
    raven_email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name=_('Raven email address'),
    )
    uid_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('UID Number'),
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
    )
    AWAITING_APPROVAL = 0
    APPROVED = 1
    DECLINED = 2
    REVOKED = 3
    SUSPENDED = 4
    CLOSED = 5
    STATUS_CHOICES = (
        (AWAITING_APPROVAL, 'Awaiting Approval'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
        (REVOKED, 'Revoked'),
        (SUSPENDED, 'Suspended'),
        (CLOSED, 'Closed'),
    )
    PRE_APPROVED_OPTIONS = [
        STATUS_CHOICES[AWAITING_APPROVAL],
        STATUS_CHOICES[APPROVED],
        STATUS_CHOICES[DECLINED],
    ]
    POST_APPROVED_OPTIONS = [
        STATUS_CHOICES[APPROVED],
        STATUS_CHOICES[REVOKED],
        STATUS_CHOICES[SUSPENDED],
        STATUS_CHOICES[CLOSED],
    ]
    account_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_APPROVAL,
        verbose_name=_('Current Status'),
    )
    previous_account_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_APPROVAL,
        verbose_name=_('Previous Status'),
    )

    def get_account_status_choices(self):
        if Profile.STATUS_CHOICES[self.account_status] in Profile.POST_APPROVED_OPTIONS:
            return Profile.POST_APPROVED_OPTIONS
        else:
            return Profile.PRE_APPROVED_OPTIONS

    def is_awaiting_approval(self):
        return True if self.account_status == Profile.AWAITING_APPROVAL else False

    def is_approved(self):
        return True if self.account_status == Profile.APPROVED else False

    def is_declined(self):
        return True if self.account_status == Profile.DECLINED else False

    def is_revoked(self):
        return True if self.account_status == Profile.REVOKED else False

    def is_suspended(self):
        return True if self.account_status == Profile.SUSPENDED else False

    def is_closed(self):
        return True if self.account_status == Profile.CLOSED else False

    @property
    def institution(self):
        """
        Return institution if shibboleth user, otherwise return None
        """
        if hasattr(self, 'shibbolethprofile'):
            return self.shibbolethprofile.institution
        else:
            return None

    def reset_account_status(self):
        """
        Reset the current account status to the previous account status.
        """
        self.account_status = self.previous_account_status
        self.save()

    def __str__(self):
        return self.user.email


class ShibbolethProfile(Profile):
    shibboleth_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Institutional address'),
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text=_('Institution user is based'),
    )
    department = models.CharField(
        max_length=128,
        blank=True,
    )
    orcid = models.CharField(
        max_length=16,
        blank=True,
        help_text=_('16-digit ORCID'),
    )
    scopus = models.URLField(
        blank=True,
        help_text=_('Scopus URL'),
    )
    homepage = models.URLField(blank=True)
    cronfa = models.URLField(
        blank=True,
        help_text=_('Cronfa URL'),
    )


class CustomUserManager(BaseUserManager):
    """
    A CustomUser manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager".
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_pending_shibbolethuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_shibboleth_login_required', True)
        extra_fields.setdefault('username', email)
        if extra_fields.get('is_staff') is not False:
            raise ValueError(_(
                'Pending ShibbolethUser must have is_staff=False.'
            ))
        if extra_fields.get('is_superuser') is not False:
            raise ValueError(_(
                'Pending ShibbolethUser must have is_superuser=False.'
            ))
        if extra_fields.get('is_shibboleth_login_required') is not True:
            raise ValueError(_(
                'Pending ShibbolethUser must have '
                'is_shibboleth_login_required=True.'
            ))
        return self._create_user(email, password, **extra_fields)


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_shibboleth_login_required', False)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('is_shibboleth_login_required') is not False:
            raise ValueError(_(
                'Superuser must have is_shibboleth_login_required=False.'
            ))
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Represents an application User.
    """

    class Meta:
        verbose_name_plural = 'Users'

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'
        ),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(unique=True, null=True)
    is_shibboleth_login_required = models.BooleanField(
        default=True,
        help_text=_(
            'Designates whether this user is required to log in '
            'via a shibboleth identity provider.'
        ),
        verbose_name=_('shibboleth login required status'),
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text=_(
            'Designates that this user has all permissions '
            'without explicitly assigning them.'
        ),
        verbose_name=_('superuser status'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(
        blank=True,
        max_length=30,
        verbose_name=_('first name'),
    )
    last_name = models.CharField(
        blank=True,
        max_length=30,
        verbose_name=_('last name'),
    )
    reason_for_account = models.TextField(
        blank=True,
        max_length=1024,
        verbose_name=_('Reason for account'),
    )
    accepted_terms_and_conditions = models.BooleanField(
        default=False,
        verbose_name=_('Terms and Conditions'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        if self.is_shibboleth_login_required:
            _, domain = self.email.split('@')
            institution = Institution.objects.get(base_domain=domain)
            ShibbolethProfile.objects.update_or_create(
                user=self,
                defaults={
                    'shibboleth_id': self.email,
                    'institution': institution,
                },
            )
        else:
            Profile.objects.update_or_create(user=self)
        self.profile.save()

    def __str__(self):
        return '{first_name} {last_name} ({email})'.format(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
        )
