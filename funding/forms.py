from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FundingSource
from .models import Publication
from .models import FundingSourceMembership

from institution.models import Institution


class FundingSourceForm(forms.ModelForm):
    class Meta:
        model = FundingSource
        fields = ['title', 'identifier', 'amount', 'funding_body', 'pi_email']

    def __init__(self, user, *args, **kwargs):
        instance = kwargs.get('instance', {})
        if hasattr(instance, 'pi') and instance.pi is not None:
            initial = kwargs.get('initial', {})
            initial['pi_email'] = instance.pi.email
            kwargs['initial'] = initial
        super(FundingSourceForm, self).__init__(*args, **kwargs)
        if user.profile.institution is not None:
            self.fields['pi_email'].label = _(
                '{} Principal Investigator Email address'.format(
                    user.profile.institution.name
                )
            )
            if user.profile.institution.funding_database_name != '':
                self.fields['identifier'].label = _(
                    '{} identifier'.format(
                        user.profile.institution.funding_database_name
                    )
                )
        # Set the initial email if pi is a user
        self.user_email = user.email

    def clean_pi_email(self):
        cleaned_data = super().clean()
        email = cleaned_data['pi_email']
        domain = email.split('@')[1]
        domains = list(Institution.objects.values_list('base_domain',flat=True))
        if domain not in domains:
            raise forms.ValidationError(_(
                'Needs to be a valid institutional email address.'
            ))
        return email


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'url']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (user.profile.institution is not None and
            user.profile.institution.local_repository_name != ''):
            self.local_repository_domain = user.profile.institution.local_repository_domain
            self.fields['url'].label = _(
                '{repo} URL of the publication'.format(
                    repo=user.profile.institution.local_repository_name
                )
            )
        else:
            self.local_repository_domain = ''

    def clean_url(self):
        url = self.cleaned_data['url']
        if self.local_repository_domain not in url:
            raise forms.ValidationError(_('URL must contain {domain}').format(
                domain=self.local_repository_domain)
            )
        return url


class FundingSourceApprovalForm(forms.ModelForm):
    class Meta:
        model = FundingSource
        fields = ['title', 'identifier', 'amount', 'funding_body', 'pi_email', 'approved']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', {})
        if hasattr(instance, 'pi') and instance.pi is not None:
            initial = kwargs.get('initial', {})
            initial['pi_email'] = instance.pi.email
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean_pi_email(self):
        cleaned_data = super().clean()
        email = cleaned_data['pi_email']
        domain = email.split('@')[1]
        domains = list(Institution.objects.values_list('base_domain',flat=True))
        if domain not in domains:
            raise forms.ValidationError(_(
                'Needs to be a valid institutional email address.'
            ))
        return email

    def clean_approved(self):
        cleaned_data = super().clean()
        approved = cleaned_data['approved']
        if not approved:
            raise forms.ValidationError(_(
                'You did not approve the funding source.'
            ))
        return approved

