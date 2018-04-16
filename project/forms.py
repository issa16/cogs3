from django import forms

from .models import Project
from .models import ProjectUserMembership


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
        ]


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
                raise forms.ValidationError("You are currently a member of the project.")
            if project.awaiting_approval():
                raise forms.ValidationError("The project is currently awaiting approval.")
            if ProjectUserMembership.objects.filter(project=project, user=user).exists():
                raise forms.ValidationError("A membership request for this project already exists.")
        except Project.DoesNotExist:
            raise forms.ValidationError("Invalid SCW project code.")
        return project_code
