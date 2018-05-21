from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from institution.models import Institution
from project.models import Project
from project.models import ProjectUserMembership


class ProjectAdminForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = '__all__'

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


class LocalizeModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return _(obj.__str__())


class ProjectCreationForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = [
            'code',
            'category',
            'status',
            'allocation_systems',
            'members',
            'tech_lead',
            'notes',
            'economic_user',
            'allocation_rse',
            'reason_decision',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'datepicker'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'datepicker'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectCreationForm, self).__init__(*args, **kwargs)
        self.fields['institution'] = LocalizeModelChoiceField(
            queryset=Institution.objects.all(),
            label=_('Institution'),
        )


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
            if project.awaiting_approval():
                raise forms.ValidationError(_("The project is currently awaiting approval."))
            if ProjectUserMembership.objects.filter(project=project, user=user).exists():
                raise forms.ValidationError(_("A membership request for this project already exists."))
        except Project.DoesNotExist:
            raise forms.ValidationError(_("Invalid Project Code."))
        return project_code
