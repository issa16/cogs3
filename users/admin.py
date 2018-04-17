from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm
from .forms import CustomUserCreationForm
from .models import CustomUser
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = (
        'username',
        'first_name',
        'last_name',
        'get_account_status',
        'get_scw_username',
        'get_shibboleth_username',
        'get_institution',
    )
    list_select_related = ('profile', )
    model = CustomUser

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': (
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ),
    }), )

    @classmethod
    def get_account_status(cls, instance):
        return Profile.STATUS_CHOICES[instance.profile.account_status - 1][1]

    get_account_status.short_description = 'Account Status'

    @classmethod
    def get_shibboleth_username(cls, instance):
        return instance.profile.shibboleth_username

    get_shibboleth_username.short_description = 'Shibboleth Username'

    @classmethod
    def get_scw_username(cls, instance):
        return instance.profile.scw_username

    get_scw_username.short_description = 'SCW Username'

    @classmethod
    def get_institution(cls, instance):
        return instance.profile.institution

    get_institution.short_description = 'Institution'

    def get_inline_instance(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instance(request, obj)
