from django import forms
from django.conf import settings
from django.db.models import Q
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from project.models import Project
from project.models import ProjectUserMembership


class FileLinkWidget(forms.Widget):

    def __init__(self, obj, attrs=None):
        self.object = obj
        super(FileLinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if self.object.pk:
            return u'<a target="_blank" href="/en/projects/applications/%s/document">Download</a>' % (self.object.id)
        else:
            return u''


class ProjectAdminForm(forms.ModelForm):

    document_download = forms.CharField(label='Download Supporting Document', required=False)

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'legacy_hpcw_id',
            'legacy_arcca_id',
            'code',
            'institution_reference',
            'department',
            'pi',
            'tech_lead',
            'category',
            'funding_source',
            'start_date',
            'end_date',
            'economic_user',
            'requirements_software',
            'requirements_gateways',
            'requirements_training',
            'requirements_onboarding',
            'allocation_rse',
            'allocation_cputime',
            'allocation_memory',
            'allocation_storage_home',
            'allocation_storage_scratch',
            'document',
            'document_download',
            'status',
            'reason_decision',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        self.initial_status = self.instance.status
        self.fields['document_download'].widget = FileLinkWidget(self.instance)

    def clean_code(self):
        """
        Ensure the project code is unique.
        """
        current_code = self.instance.code
        updated_code = self.cleaned_data['code']
        if current_code != updated_code:
            if Project.objects.filter(code=updated_code).exists():
                raise forms.ValidationError(_('Project code must be unique.'))
        return updated_code

    def clean_legacy_hpcw_id(self):
        """
        Ensure the project legacy hpcw id is unique.
        """
        current_legacy_hpcw_id = self.instance.legacy_hpcw_id
        updated_legacy_hpcw_id = self.cleaned_data['legacy_hpcw_id']
        if current_legacy_hpcw_id != updated_legacy_hpcw_id:
            if Project.objects.filter(legacy_hpcw_id=updated_legacy_hpcw_id).exists():
                raise forms.ValidationError(_('Project legacy HPCW id must be unique.'))
        return updated_legacy_hpcw_id

    def clean_legacy_arcca_id(self):
        """
        Ensure the project legacy arcca id is unique.
        """
        current_legacy_arcca_id = self.instance.legacy_arcca_id
        updated_legacy_arcca_id = self.cleaned_data['legacy_arcca_id']
        if current_legacy_arcca_id != updated_legacy_arcca_id:
            if Project.objects.filter(legacy_arcca_id=updated_legacy_arcca_id).exists():
                raise forms.ValidationError(_('Project legacy ARCCA id must be unique.'))
        return updated_legacy_arcca_id

    def save(self, commit=True):
        project = super(ProjectAdminForm, self).save(commit=False)
        if self.initial_status != project.status:
            # TODO - OpenLDAP API call
            pass
        if commit:
            project.save()
        return project


class LocalizeModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return _(obj.__str__())


class ProjectCreationForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'legacy_hpcw_id',
            'legacy_arcca_id',
            'institution_reference',
            'department',
            'pi',
            'funding_source',
            'start_date',
            'end_date',
            'requirements_software',
            'requirements_gateways',
            'requirements_training',
            'requirements_onboarding',
            'allocation_cputime',
            'allocation_memory',
            'allocation_storage_home',
            'allocation_storage_scratch',
            'document',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'datepicker'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'datepicker'
            }),
        }

    def set_user(self, user):
        self.user = user

    def clean(self):
        self.instance.tech_lead = self.user
        if self.instance.tech_lead.profile.institution is None:
            raise ValidationError('Only users which belong to an institution can create projects.')


class ProjectUserMembershipCreationForm(forms.Form):
    project_code = forms.CharField(max_length=20)

    def clean_project_code(self):
        # Verify the project code is valid and the project has been approved.
        project_code = self.cleaned_data['project_code']
        try:
            project = Project.objects.get(
                Q(code=project_code) | Q(legacy_hpcw_id=project_code) | Q(legacy_arcca_id=project_code))
            user = self.initial.get('user', None)
            # The technical lead will automatically be added as a member of the of project.
            if project.tech_lead == user:
                raise forms.ValidationError(_("You are currently a member of the project."))
            if project.is_awaiting_approval():
                raise forms.ValidationError(_("The project is currently awaiting approval."))
            if ProjectUserMembership.objects.filter(project=project, user=user).exists():
                raise forms.ValidationError(_("A membership request for this project already exists."))
        except Project.DoesNotExist:
            raise forms.ValidationError(_("Invalid Project Code."))
        return project_code


class ProjectUserMembershipAdminForm(forms.ModelForm):

    class Meta:
        model = ProjectUserMembership
        fields = '__all__'

    def save(self, commit=True):
        project_user_membership = super(ProjectUserMembershipAdminForm, self).save(commit=False)
        if 'status' in self.changed_data:
            # TODO - OpenLDAP API call
            pass
        if commit:
            project_user_membership.save()
        return project_user_membership
