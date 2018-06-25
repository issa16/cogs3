from django import forms
from .models import FundingSource
from institution.models import Institution


class FundingSourceForm(forms.ModelForm):
    class Meta:
        model = FundingSource
        fields = ['title', 'identifier', 'funding_body', 'pi_email']

    def __init__(self, user, *args, **kwargs):
        instance = kwargs.get('instance', {})
        if hasattr(instance, 'pi') and instance.pi is not None:
            initial = kwargs.get('initial', {})
            initial['pi_email'] = instance.pi.email
            kwargs['initial'] = initial
        super(FundingSourceForm, self).__init__(*args, **kwargs)
        # Set the initial email if pi is a user
        self.user_email = user.email

    def clean_pi_email(self):
        cleaned_data = super().clean()
        email = cleaned_data['pi_email']
        domain = email.split('@')[1]
        domains = list(Institution.objects.values_list('base_domain',flat=True))
        if domain not in domains:
            raise forms.ValidationError('Needs to be a valid institutional email address.')
        return email
