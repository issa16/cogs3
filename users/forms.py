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
            'title',
            'first_name',
            'last_name',
            'allow_emails',
        )
        # Give a dropdown menu for the title
        widgets = {
            'title': forms.Select(choices=[
            ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.'), ('Mr.', 'Mr.'),
            ('Dr.', 'Dr.'), ('Prof.', 'Prof.'),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        # Additionally required attributes
        self.fields['email'].required = True
        self.fields['title'].required = True
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

    class Meta:
        # Give a dropdown menu for the title
        widgets = {
            'title': forms.Select(choices=[
            ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.'), ('Mr.', 'Mr.'),
            ('Dr.', 'Dr.'), ('Prof.', 'Prof.'),
            ]),
        }


    def clean(self):
        cleaned_data = super().clean()
        is_shibboleth_login_required = cleaned_data.get('is_shibboleth_login_required')
        email = cleaned_data.get('email')
        if is_shibboleth_login_required:
            try:
                Institution.is_valid_email_address(email)
            except InvalidInstitution as e:
                raise forms.ValidationError(str(e))
