from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Permission

from institution.exceptions import InvalidInstitutionalEmailAddress
from institution.models import Institution
from users.models import CustomUser
from users.models import Profile
from users.openldap import update_openldap_user


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating a Profile instance.
    """

    class Meta:
        model = Profile
        exclude = ('previous_account_status', )

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance.user_id:
            self.initial_account_status = self.instance.account_status
            self.fields['account_status'] = forms.ChoiceField(choices=self.instance.get_account_status_choices())

    def save(self, commit=True):
        profile = super(ProfileUpdateForm, self).save(commit=False)

        # Assign the project.add permission to an approved user.
        if profile.account_status == Profile.APPROVED:
            if not profile.user.has_perm('add_project'):
                permission = Permission.objects.get(codename='add_project')
                profile.user.user_permissions.add(permission)

        # Ensure any updates to the account status are propagated to LDAP.
        profile.previous_account_status = self.initial_account_status
        if self.initial_account_status != profile.account_status:
            update_openldap_user(profile)

        if commit:
            profile.save()
        return profile


class CustomUserCreationForm(forms.ModelForm):
    """
    Form for creating a CustomUser instance.
    """

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'is_staff',
            'is_active',
            'is_shibboleth_login_required',
            'first_name',
            'last_name',
        )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # Additionally required attributes
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(CustomUser.objects.make_random_password(length=30))
        user.username = user.email
        if commit:
            user.save()
        return user

    def clean(self):
        if self.cleaned_data.get('is_shibboleth_login_required'):
            try:
                Institution.is_valid_email_address(self.cleaned_data.get('email'))
            except InvalidInstitutionalEmailAddress as e:
                raise forms.ValidationError(str(e))


class RegisterForm(forms.ModelForm):
    """
    Form for registering a new user.
    The user's email address is parsed from the idp's authorisation response.
    """

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'reason_for_account',
            'accepted_terms_and_conditions',
        )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Additionally required attributes
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['reason_for_account'].required = True
        self.fields['accepted_terms_and_conditions'].required = True


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating a CustomUser instance.
    """

    def clean(self):
        if self.cleaned_data.get('is_shibboleth_login_required'):
            try:
                Institution.is_valid_email_address(self.cleaned_data.get('email'))
            except InvalidInstitutionalEmailAddress as e:
                raise forms.ValidationError(str(e))
