from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models

from institution.models import Institution


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shibboleth_username = models.CharField(
        max_length=50,
        blank=True,
        help_text="Institutional address",
    )
    scw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="SCW username",
    )
    hpcw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="HPCW username",
    )
    hpcw_email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name="HPCW email address",
    )
    raven_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Raven username",
    )
    raven_email = models.EmailField(
        max_length=100,
        blank=True,
        verbose_name="Raven email address",
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        help_text="Institution user is based",
    )
    department = models.CharField(
        max_length=128,
        blank=True,
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
        return self.user.username


class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):

    objects = CustomUserManager()
