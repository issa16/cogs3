from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from common.util import email_user
from funding.models import Attribution, FundingSource
from institution.models import Institution
from project.models import (Project, ProjectUserMembership, RSEAllocation,
                            SystemAllocationRequest)
from project.openldap import (update_openldap_project,
                              update_openldap_project_membership)
from users.models import CustomUser

PROJECT_CODE_PREFIX = "scw"


class FileLinkWidget(forms.Widget):

    def __init__(self, obj, attrs=None):
        self.object = obj
        super(FileLinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if self.object.pk:
            return u'<a target="_blank" href="/en/projects/applications/%s/document">Download</a>' % (
                self.object.id
            )
        else:
            return u''


class SelectMultipleTickbox(forms.widgets.CheckboxSelectMultiple):
    template_name = 'project/attributionwidget.html'


class ProjectAdminForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'legacy_hpcw_id',
            'legacy_arcca_id',
            'institution_reference',
            'department',
            'gid_number',
            'supervisor_name',
            'supervisor_position',
            'supervisor_email',
            'approved_by_supervisor',
            'attributions',
            'tech_lead',
            'category',
            'economic_user',
            'custom_user_cap',
        ]

    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)

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
        Ensure the project legacy HPCW id is unique.
        """
        current_legacy_hpcw_id = self.instance.legacy_hpcw_id
        updated_legacy_hpcw_id = self.cleaned_data['legacy_hpcw_id']
        if updated_legacy_hpcw_id.startswith(PROJECT_CODE_PREFIX):
            raise forms.ValidationError(_('SCW Project codes are reserved.'))
        if current_legacy_hpcw_id != updated_legacy_hpcw_id:
            if Project.objects.filter(legacy_hpcw_id=updated_legacy_hpcw_id
                                     ).exists():
                raise forms.ValidationError(_('Project legacy HPCW id must be unique.'))
        return updated_legacy_hpcw_id

    def clean_legacy_arcca_id(self):
        """
        Ensure the project legacy ARCCA id is unique.
        """
        current_legacy_arcca_id = self.instance.legacy_arcca_id
        updated_legacy_arcca_id = self.cleaned_data['legacy_arcca_id']
        if updated_legacy_arcca_id.startswith(PROJECT_CODE_PREFIX):
            raise forms.ValidationError(_('SCW Project codes are reserved.'))
        if current_legacy_arcca_id != updated_legacy_arcca_id:
            if Project.objects.filter(legacy_arcca_id=updated_legacy_arcca_id
                                     ).exists():
                raise forms.ValidationError(_('Project legacy ARCCA id must be unique.'))
        return updated_legacy_arcca_id

    def save(self, commit=True):
        project = super(ProjectAdminForm, self).save(commit=False)
        if commit:
            project.save()
        return project


class SystemAllocationRequestAdminForm(forms.ModelForm):

    document_download = forms.CharField(
        label=_('Download Supporting Document'),
        required=False
    )

    class Meta:
        model = SystemAllocationRequest
        fields = [
            'project',
            'information',
            'start_date',
            'end_date',
            'allocation_rse',
            'allocation_cputime',
            'allocation_memory',
            'allocation_storage_home',
            'allocation_storage_scratch',
            'requirements_software',
            'requirements_training',
            'requirements_onboarding',
            'document',
            'document_download',
            'status',
            'reason_decision',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        super(SystemAllocationRequestAdminForm, self).__init__(*args, **kwargs)
        self.initial_status = self.instance.status
        self.fields['document_download'].widget = FileLinkWidget(self.instance)
        self.fields['status'] = forms.ChoiceField(
            choices=self._get_status_choices(self.instance.status)
        )
        if self.instance.id is None:
            self.fields['status'] = forms.ChoiceField(
                choices=[Project.STATUS_CHOICES[Project.AWAITING_APPROVAL]]
            )

    def _get_status_choices(self, status):
        pre_approved_options = [
            Project.STATUS_CHOICES[Project.AWAITING_APPROVAL],
            Project.STATUS_CHOICES[Project.APPROVED],
            Project.STATUS_CHOICES[Project.DECLINED],
        ]
        post_approved_options = [
            Project.STATUS_CHOICES[Project.APPROVED],
            Project.STATUS_CHOICES[Project.REVOKED],
            Project.STATUS_CHOICES[Project.SUSPENDED],
            Project.STATUS_CHOICES[Project.CLOSED],
        ]
        if Project.STATUS_CHOICES[status] in post_approved_options:
            return post_approved_options
        else:
            return pre_approved_options

    def save(self, commit=True):
        allocation = super(SystemAllocationRequestAdminForm,
                           self).save(commit=False)
        allocation.previous_status = self.initial_status
        if self.initial_status != allocation.status:
            update_openldap_project(allocation)
        if commit:
            allocation.save()
        return allocation


class LocalizeModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return _(obj.__str__())


class ProjectCreationForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'institution_reference',
            'department',
            'supervisor_name',
            'supervisor_position',
            'supervisor_email',
            'attributions',
        ]

    def __init__(self, user, *args, **kwargs):
        super(ProjectCreationForm, self).__init__(*args, **kwargs)
        self.user = user
        if self.user.profile.institution is not None and not self.user.profile.institution.needs_funding_workflow:
            del self.fields['attributions']
        else:
            self.fields['attributions'] = forms.ModelMultipleChoiceField(
                label='',
                widget=SelectMultipleTickbox(),
                queryset=Attribution.objects.filter(
                    created_by=self.user
                ),
                required=False,
            )

    def clean_supervisor_email(self):
        cleaned_data = super().clean()
        try:
            email = cleaned_data['supervisor_email']
            domain = email.split('@')[1]
            if Institution.objects.filter(base_domain=domain).exists():
                return email
        except:
            pass
        raise forms.ValidationError(_(
            'Please enter an institutional email address ending '
            'with one of: ' + ', '.join(
                '@' + institution.base_domain
                for institution in Institution.objects.all()
            ) + '.'
        ))

    def clean(self):
        self.instance.tech_lead = self.user
        if self.instance.tech_lead.profile.institution is None:
            raise forms.ValidationError(_(
                'Only users which belong to an institution can create projects.'
            ))


class ProjectAssociatedForm(forms.ModelForm):

    def __init__(
        self, user, include_project=True, project=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.user = user
        if project:
            self.fields['project'].initial = project
            self.fields['project'].widget = forms.HiddenInput()
        elif include_project:
            self.fields['project'] = forms.ModelChoiceField(
                queryset=Project.objects.filter(tech_lead=user)
            )
        else:
            del self.fields['project']

    def clean_project(self):
        if self.cleaned_data['project'].tech_lead != self.user:
            raise forms.ValidationError(_('Selected project not found.'))
        return self.cleaned_data['project']


class ProjectManageAttributionForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['attributions']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        owned_attributions = Attribution.objects.filter(owner=self.user,)
        # Also get funding sources the user is a member of
        fundingsources = Attribution.objects.filter(
            fundingsource__in=FundingSource.objects.
            filter(fundingsourcemembership__user=self.user,)
        )
        self.fields['attributions'] = forms.ModelMultipleChoiceField(
            label='',
            widget=SelectMultipleTickbox(),
            queryset=(owned_attributions | fundingsources),
            required=False,
        )


class ProjectSupervisorApproveForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['approved_by_supervisor']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        if self.instance.supervisor_email != self.user.email:
            raise forms.ValidationError(_(
                'You are not the supervisor of this project.'
            ))


class SystemAllocationRequestCreationForm(ProjectAssociatedForm):

    class Meta:
        model = SystemAllocationRequest
        fields = [
            'information',
            'start_date',
            'end_date',
            'allocation_cputime',
            'allocation_memory',
            'allocation_storage_home',
            'allocation_storage_scratch',
            'requirements_software',
            'requirements_training',
            'requirements_onboarding',
            'document',
            'project',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class RSEAllocationRequestCreationForm(ProjectAssociatedForm):

    class Meta:
        model = RSEAllocation
        fields = [
            'title',
            'duration',
            'goals',
            'software',
            'outcomes',
            'confidentiality',
            'project',
        ]

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        if self.user.profile.institution.rse_notify_email:
            user_name = ' '.join((self.user.first_name, self.user.last_name))
            subject = _(
                'New RSE time request from {}'.format(user_name)
            )
            context = {
                'user': user_name,
                'to': self.user.profile.institution.rse_notify_email,
                'title': self.cleaned_data['title'],
                'duration': self.cleaned_data['duration'],
                'goals': self.cleaned_data['goals'],
                'software': self.cleaned_data['software'],
                'outcomes': self.cleaned_data['outcomes'],
                'confidentiality': self.cleaned_data['confidentiality'],
            }
            text_template_path = 'notifications/project/rse_request.txt'
            html_template_path = 'notifications/project/rse_request.html'
            email_user(subject, context, text_template_path, html_template_path)
        return result


class ProjectUserMembershipCreationForm(forms.Form):
    project_code = forms.CharField(max_length=20)

    def clean_project_code(self):
        # Verify the project code is valid and the project has been approved.
        project_code = self.cleaned_data['project_code']
        try:
            project = Project.objects.get(
                Q(code=project_code) | Q(legacy_hpcw_id=project_code) |
                Q(legacy_arcca_id=project_code)
            )
            user = self.initial.get('user', None)
            # The technical lead will automatically be added as a member of the of project.
            if project.tech_lead == user:
                raise forms.ValidationError(_("You are currently a member of the project."))
            if ProjectUserMembership.objects.filter(
                project=project, user=user
            ).exists():
                raise forms.ValidationError(_("A membership request for this project already exists."))
        except Project.DoesNotExist:
            raise forms.ValidationError(_("Invalid Project Code."))
        return project_code


class ProjectUserInviteForm(forms.Form):
    email = forms.CharField(max_length=50)
    initiated_by_user = False

    def clean_email(self):
        # Verify that the user exists and the project is approved
        email = self.cleaned_data['email']
        project = Project.objects.filter(id=self.initial['project_id']).first()
        user = CustomUser.objects.filter(email=email).first()
        # The technical lead will automatically be added as a member of the of project.
        if not user:
            raise forms.ValidationError(_("No user exists with given email."))
        if project.tech_lead == user:
            raise forms.ValidationError(_("You are currently a member of the project."))
        if ProjectUserMembership.objects.filter(
            project=project, user=user
        ).exists():
            raise forms.ValidationError(_("A membership request for this project already exists."))
        if not project.can_have_more_users():
            raise forms.ValidationError(_(
                "This project has reached its membership cap. "
                "If you require more members, please contact support."
            ))
        return email


class ProjectUserMembershipAdminForm(forms.ModelForm):

    class Meta:
        model = ProjectUserMembership
        fields = [
            'project',
            'user',
            'status',
            'initiated_by_user',
            'date_joined',
            'date_left',
        ]

    def __init__(self, *args, **kwargs):
        super(ProjectUserMembershipAdminForm, self).__init__(*args, **kwargs)
        self.initial_status = self.instance.status
        self.fields['status'] = forms.ChoiceField(
            choices=self._get_status_choices(self.instance.status)
        )

    def _get_status_choices(self, status):
        # yapf: disable
        pre_approved_options = [
            ProjectUserMembership.STATUS_CHOICES[ProjectUserMembership.AWAITING_AUTHORISATION],
            ProjectUserMembership.STATUS_CHOICES[ProjectUserMembership.AUTHORISED],
            ProjectUserMembership.STATUS_CHOICES[ProjectUserMembership.DECLINED],
        ]
        post_approved_options = [
            ProjectUserMembership.STATUS_CHOICES[ProjectUserMembership.AUTHORISED],
            ProjectUserMembership.STATUS_CHOICES[ProjectUserMembership.REVOKED],
            ProjectUserMembership.STATUS_CHOICES[ProjectUserMembership.SUSPENDED],
        ]
        if ProjectUserMembership.STATUS_CHOICES[status] in post_approved_options:
            return post_approved_options
        else:
            return pre_approved_options
        # yapf: enable

    def clean_status(self):
        if (
            self.initial_status != ProjectUserMembership.AWAITING_AUTHORISED and
            self.cleaned_data['status'] == ProjectUserMembership.AUTHORISED
        ):
            if not self.cleaned_data['project'].can_have_more_users():
                raise forms.ValidationError(_(
                    "This project has reached its membership cap. "
                    "If you require more members, please contact support."
                ))

    def save(self, commit=True):
        project_user_membership = super(ProjectUserMembershipAdminForm,
                                        self).save(commit=False)
        if self.initial_status != project_user_membership.status:
            if project_user_membership.status == ProjectUserMembership.AUTHORISED:
                user = project_user_membership.user
                if user.profile.institution and user.profile.institution.needs_user_approval:
                    user.profile.activate()
            update_openldap_project_membership(project_user_membership)
        if commit:
            project_user_membership.save()
        return project_user_membership
