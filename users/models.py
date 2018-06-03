from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from institution.models import Institution


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    scw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='SCW username',
    )
    hpcw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='HPCW username',
    )
    hpcw_email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name='HPCW email address',
    )
    raven_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Raven username',
    )
    raven_email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name='Raven email address',
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
    )
    AWAITING_APPROVAL = 1
    APPROVED = 2
    DECLINED = 3
    REVOKED = 4
    SUSPENDED = 5
    CLOSED = 6
    STATUS_CHOICES = (
        (AWAITING_APPROVAL, 'Awaiting Approval'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined'),
        (REVOKED, 'Revoked'),
        (SUSPENDED, 'Suspended'),
        (CLOSED, 'Closed'),
    )
    account_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=AWAITING_APPROVAL,
    )

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __str__(self):
        return self.user.email


class ShibbolethProfile(Profile):
    shibboleth_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Institutional address',
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text='Institution user is based',
    )
    department = models.CharField(
        max_length=128,
        blank=True,
    )
    orcid = models.CharField(
        max_length=16,
        blank=True,
        help_text='16-digit ORCID',
    )
    scopus = models.URLField(
        blank=True,
        help_text='Scopus URL',
    )
    homepage = models.URLField(blank=True)
    cronfa = models.URLField(
        blank=True,
        help_text='Cronfa URL',
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
            raise ValueError('The Email must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_shibboleth_login_required', False)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_shibboleth_login_required') is not False:
            raise ValueError('Superuser must have is_shibboleth_login_required=False.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    email = models.EmailField(unique=True, null=True)
    is_shibboleth_login_required = models.BooleanField(
        default=True,
        help_text='Designates whether this user is required to login via a shibboleth identity provider.',
        verbose_name='shibboleth login required status',
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.',
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text='Designates that this user has all permissions without explicitly assigning them.',
        verbose_name='superuser status',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(
        blank=True,
        max_length=5,
        verbose_name='title',
    )
    first_name = models.CharField(
        blank=True,
        max_length=30,
        verbose_name='first name',
    )
    last_name = models.CharField(
        blank=True,
        max_length=30,
        verbose_name='last name',
    )
    allow_emails = models.BooleanField(
        default=False,
        help_text='Wether the user has given permission for us to send emails',
        verbose_name='allow emails',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def notify(self, title, message):
        """Send a message to user
        Sends an email if the user has opted in. Otherwise there is
        no notification

        Parameters
        ----------
        title : type
            The title of the message or subject of the email
        message : type
            Main content of the message
        """
        if self.allow_emails:
            sender = 'support@supercomputing.wales';
            plaintext = get_template('notifications/email_base.txt')
            html = get_template('notifications/email_base.html')
            context = {
                'title': self.title,
                'last_name': self.last_name,
                'message_title': title,
                'message': message,
            }
            text_email = plaintext.render(context)
            html_email = html.render(context)
            email = EmailMultiAlternatives(
                title, text_email, sender, [self.email],
            )
            email.attach_alternative(html_email, "text/html")
            email.send(fail_silently=True)

    class Meta:
        verbose_name_plural = 'Users'
