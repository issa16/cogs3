from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms.models import BaseInlineFormSet

from openldap.api import user_api
from users.forms import CustomUserChangeForm
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from users.models import Profile
from users.models import ShibbolethProfile


class ProfileInlineFormset(BaseInlineFormSet):

    def save_existing(self, form, instance, commit=True):
        profile = super(ProfileInlineFormset, self).save_existing(form, instance, commit)
        if 'account_status' in form.changed_data:
            user_api.update_user_openldap_account(profile)
        if commit:
            profile.save()
        return profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    formset = ProfileInlineFormset


class ShibbolethProfileInline(admin.StackedInline):
    model = ShibbolethProfile
    can_delete = False
    verbose_name_plural = 'Shibboleth Profile'
    fk_name = 'user'
    formset = ProfileInlineFormset


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Form to add or update a CustomUser instance.
    """

    def activate_users(self, request, queryset):
        rows_updated = 0
        for user in queryset:
            user.profile.account_status = Profile.APPROVED
            user.save()
            user_api.update_user_openldap_account(user.profile)
            rows_updated += 1
        message = self._account_action_message(rows_updated)
        self.message_user(request, '{message} successfully activated.'.format(message=message))

    activate_users.short_description = 'Activate selected users {company_name} account'.format(
        company_name=settings.COMPANY_NAME)

    def deactivate_users(self, request, queryset):
        rows_updated = 0
        for user in queryset:
            user.profile.account_status = Profile.SUSPENDED
            user.save()
            user_api.update_user_openldap_account(user.profile)
            rows_updated += 1
        message = self._account_action_message(rows_updated)
        self.message_user(request, '{message} successfully deactivated.'.format(message=message))

    deactivate_users.short_description = 'Deactivate selected users {company_name} account'.format(
        company_name=settings.COMPANY_NAME)

    def _account_action_message(self, rows_updated):
        if rows_updated == 1:
            message = '1 {company_name} account was'.format(company_name=settings.COMPANY_NAME)
        else:
            message = '{rows} {company_name} accounts were'.format(
                rows=rows_updated,
                company_name=settings.COMPANY_NAME,
            )
        return message

    def get_form(self, request, user=None, **kwargs):
        """
        Load the ShibbolethProfileInline for shibboleth users.
        Load the ProfileInline for non shibboleth users.
        """
        if user:
            if user.is_shibboleth_login_required:
                self.inlines = [ShibbolethProfileInline]
            else:
                self.inlines = [ProfileInline]
        else:
            self.inlines = []

        return super(CustomUserAdmin, self).get_form(request, user, **kwargs)

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    actions = [activate_users, deactivate_users]

    # Fields to be used when displaying a CustomUser model.
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

    search_fields = ('email', )
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

    def get_inline_instance(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instance(request, obj)
