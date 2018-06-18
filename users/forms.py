from django import forms
from django.contrib.auth.forms import UserChangeForm

from institution.exceptions import InvalidInstitution
from institution.models import Institution
from users.models import CustomUser


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
        cleaned_data = super().clean()
        is_shibboleth_login_required = cleaned_data.get('is_shibboleth_login_required')
        email = cleaned_data.get('email')
        if is_shibboleth_login_required:
            try:
                Institution.is_valid_email_address(email)
            except InvalidInstitution as e:
                raise forms.ValidationError(str(e))


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating CustomUser instances.
    """

    def clean(self):
        cleaned_data = super().clean()
        is_shibboleth_login_required = cleaned_data.get('is_shibboleth_login_required')
        email = cleaned_data.get('email')
        if is_shibboleth_login_required:
            try:
                Institution.is_valid_email_address(email)
            except InvalidInstitution as e:
                raise forms.ValidationError(str(e))


class CustomUserPersonalInfoUpdateForm(forms.ModelForm):
    """
    Form for updating Personal Information.
    """
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
        )
        exclude = ['password']
