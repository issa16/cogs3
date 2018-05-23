from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from institution.models import Institution
from project.models import Project
from project.models import ProjectUserMembership
from project.notifications import ProjectEmailNotification


class ProjectAdminForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        self.initial_status = self.instance.status

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

    def save(self, commit=True):
        project = super(ProjectAdminForm, self).save(commit=False)
        # When the project status is changed, send an email to technical lead.
        if self.initial_status != project.status:
            ProjectEmailNotification(project).send()
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
            'institution',
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
            'allocation_storage_scratch'
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
            project = Project.objects.get(code=project_code)
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
