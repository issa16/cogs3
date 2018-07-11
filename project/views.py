import datetime
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.edit import FormView

from users.models import CustomUser

from project.forms import ProjectCreationForm
from project.forms import ProjectUserInviteForm
from project.forms import ProjectUserMembershipCreationForm
from project.models import Project
from project.models import ProjectUserMembership
from project.openldap import update_openldap_project_membership


class PermissionAndLoginRequiredMixin(PermissionRequiredMixin):
    """
    CBV mixin which extends the PermissionRequiredMixin to verify
    that the user is logged in and performs a separate action if not
    """

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('home'))

    def handle_not_logged_in(self):
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_not_logged_in()
        return super(PermissionAndLoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProjectCreateView(PermissionAndLoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    form_class = ProjectCreationForm
    success_url = reverse_lazy('project-application-list')
    success_message = _('Successfully submitted a project application.')
    template_name = 'project/create.html'
    permission_required = 'project.add_project'

    def get_form(self, form_class=None):
        """
        Return an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())


class ProjectListView(PermissionAndLoginRequiredMixin, generic.ListView):
    context_object_name = 'projects'
    model = Project
    paginate_by = 50
    template_name = 'project/applications.html'
    permission_required = 'project.add_project'
    ordering = ['-created_time']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        return queryset.filter(Q(tech_lead=user))


class ProjectDetailView(PermissionAndLoginRequiredMixin, generic.DetailView):
    context_object_name = 'project'
    model = Project
    template_name = 'project/application_detail.html'
    permission_required = 'project.add_project'


class ProjectDocumentView(LoginRequiredMixin, generic.DetailView):

    def user_passes_test(self, request):
        if Project.objects.filter(id=self.kwargs['pk'], tech_lead=self.request.user).exists():
            return True
        else:
            return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('project-application-list'))
        project = Project.objects.get(id=self.kwargs['pk'])
        filename = os.path.join(settings.MEDIA_ROOT, project.document.name)
        with open(filename, 'rb') as f:
            data = f.read()
        response = HttpResponse(data, content_type=mimetypes.guess_type(filename)[0])
        response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(filename) + '"'
        return response


class ProjectUserMembershipFormView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    form_class = ProjectUserMembershipCreationForm
    success_url = reverse_lazy('project-membership-list')
    success_message = _("Successfully submitted a project membership request.")
    template_name = 'project/membership/create.html'

    def get_initial(self):
        data = super().get_initial()
        data.update({'user': self.request.user})
        return data

    def form_valid(self, form):
        project_code = form.cleaned_data['project_code']
        project = Project.objects.get(
            code=project_code,
            status=Project.APPROVED,
        )
        ProjectUserMembership.objects.create(
            project=project,
            user=self.request.user,
            date_joined=datetime.date.today(),
        )
        return super().form_valid(form)


class ProjectUserRequestMembershipListView(PermissionAndLoginRequiredMixin, generic.ListView):
    context_object_name = 'project_user_membership_requests'
    paginate_by = 50
    model = ProjectUserMembership
    template_name = 'project/membership/requests.html'
    permission_required = 'project.change_projectusermembership'
    ordering = ['-created_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        projects = Project.objects.filter(
            tech_lead=self.request.user,
            status=Project.APPROVED,
        )
        queryset = queryset.filter(project__in=projects)
        # Omit the user's membership request
        return queryset.exclude(user=self.request.user)


class ProjectUserRequestMembershipUpdateView(PermissionAndLoginRequiredMixin, generic.UpdateView):
    success_url = reverse_lazy('project-user-membership-request-list')
    context_object_name = 'project_user_membership_requests'
    model = ProjectUserMembership
    fields = ['status']
    permission_required = 'project.change_projectusermembership'
    ordering = ['date_joined']

    def request_allowed(self, request):
        # Ensure the project belongs to the user attempting to update the membership status
        try:
            project_id = request.POST.get('project_id')
            request_id = request.POST.get('request_id')
            status = int(request.POST.get('status'))
            user = self.request.user
            project = Project.objects.get(id=project_id)
            membership = ProjectUserMembership.objects.get(id=request_id)
            if membership.is_user_editable() and user == membership.user:
                allowed_states = [
                    ProjectUserMembership.AUTHORISED,
                    ProjectUserMembership.DECLINED,
                ]
                if status in allowed_states:
                    return True
            condition = membership.is_owner_editable() and project.tech_lead == user
            return condition
        except Exception:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.request_allowed(request):
            return HttpResponseRedirect(reverse('project-membership-list'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'status' in form.changed_data:
            update_openldap_project_membership(project_membership=form.instance)
        if self.request.is_ajax():
            return JsonResponse({'message': 'Successfully updated.'})
        else:
            return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response


class ProjectUserMembershipListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'project_memberships'
    template_name = 'project/memberships.html'
    model = ProjectUserMembership
    paginate_by = 50
    ordering = ['-modified_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset.filter(project__status=Project.APPROVED)


class ProjectMembesrshipInviteView(PermissionRequiredMixin, SuccessMessageMixin, LoginRequiredMixin, FormView):
    ''' As tech lead, invite a user to the a project using an email address '''
    permission_required = 'project.change_projectusermembership'
    form_class = ProjectUserInviteForm
    success_message = _("Successfully submitted an invitation.")
    template_name = 'project/membership/invite.html'
    model = Project

    def get_initial(self):
        data = super().get_initial()
        data.update({'project_id': self.kwargs['pk']})
        return data

    def get_success_url(self):
        return reverse_lazy('project-application-detail', args = [self.kwargs['pk']])

    def project_passes_test(self, request):
        try:
            project = Project.objects.filter(
                id=self.kwargs['pk'],
                tech_lead=self.request.user
            ).first()
            return project.is_approved()
        except Exception:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.project_passes_test(request):
            return HttpResponseRedirect(reverse_lazy('project-application-detail', args = [self.kwargs['pk']]))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        project = Project.objects.filter(id=self.kwargs['pk']).first()
        user = CustomUser.objects.filter(email=email).first()
        ProjectUserMembership.objects.create(
            project=project,
            user=user,
            initiated_by_user=False,
            date_joined=datetime.date.today(),
        )
        return super().form_valid(form)
