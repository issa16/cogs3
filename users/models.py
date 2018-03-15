from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shibboleth_username = models.CharField(
        max_length=50,
        blank=True,
    )
    scw_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='SCW username',
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
    account_status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=AWAITING_APPROVAL)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
        
    def __str__(self):
        return self.user.username

class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):

    objects = CustomUserManager()
