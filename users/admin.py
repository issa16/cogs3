from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms.models import BaseInlineFormSet

from users.forms import CustomUserChangeForm
from users.forms import CustomUserCreationForm
from users.forms import ProfileUpdateForm
from users.models import CustomUser
from users.models import Profile
from users.models import ShibbolethProfile
from users.openldap import update_openldap_user


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    form = ProfileUpdateForm


class ShibbolethProfileInline(admin.StackedInline):
    model = ShibbolethProfile
    can_delete = False
    verbose_name_plural = 'Shibboleth Profile'
    fk_name = 'user'
    form = ProfileUpdateForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Form to add or update a CustomUser instance.
    """

    def _account_action_message(self, rows_updated):
        if rows_updated == 1:
            message = '1 account was'
        else:
            message = '{rows} accounts were'.format(rows=rows_updated)
        return message

    def activate_users(self, request, queryset):
        rows_updated = 0
        for user in queryset:
            user.profile.account_status = Profile.APPROVED
            user.save()
            update_openldap_user(user.profile)
            rows_updated += 1
        message = self._account_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for activation.'.format(message=message))

    activate_users.short_description = 'Activate selected users account in LDAP'

    def deactivate_users(self, request, queryset):
        rows_updated = 0
        for user in queryset:
            user.profile.account_status = Profile.REVOKED
            user.save()
            update_openldap_user(user.profile)
            rows_updated += 1
        message = self._account_action_message(rows_updated)
        self.message_user(request, '{message} successfully submitted for deactivation.'.format(message=message))

    deactivate_users.short_description = 'Deactivate selected users account in LDAP'

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    actions = [activate_users, deactivate_users]

    # Fields to be used when displaying a CustomUser instance.
    list_display = (
        'email',
        'created_at',
        'get_account_status',
        'first_name',
        'last_name',
        'is_staff',
        'is_shibboleth_login_required',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # Fields to be displayed when updating a CustomUser instance.
    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password',
            )
        }),
        ('Personal info', {
            'fields': (
                'first_name',
                'last_name',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_shibboleth_login_required',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {
            'fields': (
                'last_login',
                'created_at',
                'updated_at',
            )
        }),
    )

    # Fields to be displayed when creating a CustomUser instance.
    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': (
            'email',
            'first_name',
            'last_name',
            'is_shibboleth_login_required',
        ),
    }), )
    search_fields = (
        'email',
        'first_name',
        'last_name',
        'profile__scw_username',
        'profile__hpcw_username',
        'profile__raven_username',
    )
    ordering = ('created_at', )
    list_filter = (
        'is_shibboleth_login_required',
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
    )

    @classmethod
    def get_account_status(cls, instance):
        return instance.profile.get_account_status_display()

    get_account_status.short_description = 'Account Status'

    @classmethod
    def get_scw_username(cls, instance):
        return instance.profile.scw_username

    get_scw_username.short_description = 'SCW Username'

    def get_form(self, request, user=None, **kwargs):
        if not user:
            self.inlines = []
        else:
            if user.is_shibboleth_login_required:
                self.inlines = [ShibbolethProfileInline]
            else:
                self.inlines = [ProfileInline]
        return super(CustomUserAdmin, self).get_form(request, user, **kwargs)
