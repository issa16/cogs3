import datetime
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
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
from project.forms import ProjectManageAttributionForm
from project.forms import ProjectSupervisorApproveForm
from project.forms import SystemAllocationRequestCreationForm
from project.forms import RSEAllocationRequestCreationForm
from project.forms import ProjectUserInviteForm
from project.forms import ProjectUserMembershipCreationForm
from project.models import Project
from project.models import SystemAllocationRequest
from project.models import RSEAllocation
from project.models import ProjectUserMembership
from project.notifications import project_membership_created
from project.notifications import supervisor_project_created_notification
from project.openldap import update_openldap_project_membership
from funding.models import Attribution
from funding.models import FundingSource
from common.util import email_user


def list_attributions(request, pk=None):
    owned_attributions = Attribution.objects.filter(owner=request.user)

    id_list = []
    already_attributed = Project.objects.exclude(attributions=None)
    if pk:
        already_attributed = already_attributed.exclude(id=pk)

    for A in already_attributed:
        for B in A.attributions.all():
            id_list.append(B.id)
    No_attributions = Attribution.objects.exclude(pk__in=id_list)

    # Add any fundingsources with an approved user membership
    fundingsources = Attribution.objects.filter(
        fundingsource__in=FundingSource.objects.
        filter(fundingsourcemembership__user=request.user,)
    )

    owned_attributions = (owned_attributions | fundingsources) & No_attributions
    values = [{
        'title': a.string(request.user),
        'id': a.id,
        'type': a.type
    } for a in owned_attributions]
    return JsonResponse({'results': list(values)})


class PermissionAndLoginRequiredMixin(PermissionRequiredMixin):
    """
    CBV mixin which extends the PermissionRequiredMixin to verify
    that the user is logged in and performs a separate action if not
    """

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('home'))

    def handle_not_logged_in(self):
        return redirect_to_login(
            self.request.get_full_path(), self.get_login_url(),
            self.get_redirect_field_name()
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_not_logged_in()
        response = super(PermissionAndLoginRequiredMixin,
                         self).dispatch(request, *args, **kwargs)
        return response


class AllocationCreateView(
    PermissionAndLoginRequiredMixin, SuccessMessageMixin, generic.CreateView
):

    def get_form(self, form_class=None):
        """
        Return an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())


class ProjectCreateView(AllocationCreateView):
    form_class = ProjectCreationForm
    success_message = _('Successfully submitted a project application. ' +
                        'You may now want to request supercomputer access or RSE time using the buttons below. Once the project has been approved, you will be able to add users to your project using the invite button.')
    template_name = 'project/create.html'
    permission_required = 'project.add_project'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        project = self.object
        institution = project.tech_lead.profile.institution
        if institution.needs_supervisor_approval:
            supervisor_project_created_notification.delay(project)
        return response

    def get_success_url(self):
        return reverse_lazy('project-application-detail', args=[self.object.id])


class ProjectAddAttributionView(
    PermissionAndLoginRequiredMixin, generic.UpdateView
):
    form_class = ProjectManageAttributionForm
    context_object_name = 'project'
    model = Project
    template_name = 'project/add_attributions.html'
    permission_required = 'project.add_project'

    def get_form(self, form_class=None):
        """
        Return an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse_lazy(
            'project-application-detail', args=[self.kwargs['pk']]
        )

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ProjectSupervisorApproveView(SuccessMessageMixin, generic.UpdateView):
    context_object_name = 'project'
    model = Project
    template_name = 'project/supervisor_approve.html'
    success_message = _('Thank you. The project has been submitted to Supercomputing Wales')
    redirect_field_name = '3'

    def request_allowed(self, request):
        # Check that the user is the supervisor
        project = self.get_object()
        try:
            return project.supervisor_email == request.user.email
        except Exception:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.request_allowed(request):
            return HttpResponseRedirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return ProjectSupervisorApproveForm(
            self.request.user, **self.get_form_kwargs()
        )

    def get_success_url(self):
        return reverse_lazy(
            'project-application-detail', args=[self.kwargs['pk']]
        )

    def form_valid(self, form):
        project = form.save(commit=False)
        project.approved_by_supervisor = True
        return super().form_valid(form)


class SystemAllocationCreateView(AllocationCreateView):
    form_class = SystemAllocationRequestCreationForm
    success_url = reverse_lazy('project-application-list')
    success_message = _('Successfully submitted a system allocation application.')
    template_name = 'project/createallocation.html'
    permission_required = 'project.add_project'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.kwargs.get('project', None)
        return kwargs


class RSEAllocationCreateView(AllocationCreateView):
    form_class = RSEAllocationRequestCreationForm
    success_url = reverse_lazy('rse-allocation-list')
    success_message = _('Successfully submitted an RSE time allocation application.')
    template_name = 'project/rse_time.html'
    permission_required = 'project.add_project'

    def request_allowed(self, request):
        project = Project.objects.get(id=self.kwargs['project'])

        if not project.can_request_rse_allocation(self.request.user):
            return False

        try:
            return (
                request.user.profile.institution.allows_rse_requests and
                ProjectUserMembership.objects.filter(
                    user=self.request.user, project=self.kwargs['project']
                ).exists()
            )
        except Exception:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_not_logged_in()
        if not self.request_allowed(request):
            return HttpResponseRedirect(
                reverse(
                    'project-application-detail', args=[self.kwargs['project']]
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.kwargs.get('project', None)
        return kwargs


class ProjectAndAllocationCreateView(
    PermissionAndLoginRequiredMixin, generic.TemplateView
):
    http_method_names = ['get', 'post']
    template_name = 'project/createprojectandallocation.html'
    permission_required = 'project.add_project'
    success_message = _('Successfully submitted a project application.')

    def get_context_data(self, **kwargs):
        context = super(ProjectAndAllocationCreateView,
                        self).get_context_data(**kwargs)

        if 'project_form' in kwargs:
            context['project_form'] = kwargs['project_form']
        else:
            context['project_form'] = ProjectCreationForm(self.request.user)
        if 'allocation_form' in kwargs:
            context['allocation_form'] = kwargs['allocation_form']
        else:
            context['allocation_form'] = SystemAllocationRequestCreationForm(
                self.request.user
            )
            # These two fields are unnecessary in the combined view
            del context['allocation_form'].fields['information']
            del context['allocation_form'].fields['project']

        return context

    def post(self, request):
        project_form = ProjectCreationForm(request.user, data=request.POST)
        allocation_form = SystemAllocationRequestCreationForm(
            request.user,
            include_project=False,
            data=request.POST,
            files=request.FILES
        )

        if project_form.is_valid() and allocation_form.is_valid():
            project = project_form.save()

            allocation = allocation_form.save(commit=False)
            allocation.project = project

            allocation.save()
            institution = project.tech_lead.profile.institution
            if institution.needs_supervisor_approval:
                supervisor_project_created_notification.delay(project)

            messages.success(self.request, self.success_message)
            return HttpResponseRedirect(reverse('project-application-list'))

        return self.render_to_response(
            self.get_context_data(
                project_form=project_form, allocation_form=allocation_form
            )
        )


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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.can_view_project(request.user):
            raise PermissionDenied

        return super().get(request, *args, **kwargs)


class SystemAllocationRequestDetailView(
    PermissionAndLoginRequiredMixin, generic.DetailView
):
    context_object_name = 'allocation'
    model = SystemAllocationRequest
    template_name = 'project/allocation_detail.html'
    permission_required = 'project.add_project'


class RSEAllocationRequestDetailView(
    PermissionAndLoginRequiredMixin, generic.DetailView
):
    context_object_name = 'allocation'
    model = RSEAllocation
    template_name = 'project/rse_detail.html'
    permission_required = 'project.add_project'


class ProjectDocumentView(LoginRequiredMixin, generic.DetailView):

    def user_passes_test(self, request):
        if self.request.user.is_anonymous:
            return False
        if SystemAllocationRequest.objects.filter(
            id=self.kwargs['pk'], project__tech_lead=self.request.user
        ).exists():
            return True
        else:
            return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('project-application-list'))
        allocation = SystemAllocationRequest.objects.get(id=self.kwargs['pk'])
        filename = os.path.join(settings.MEDIA_ROOT, allocation.document.name)
        with open(filename, 'rb') as f:
            data = f.read()
        response = HttpResponse(
            data, content_type=mimetypes.guess_type(filename)[0]
        )
        response['Content-Disposition'
                ] = 'attachment; filename="' + os.path.basename(filename) + '"'
        return response


class ProjectUserMembershipFormView(
    SuccessMessageMixin, LoginRequiredMixin, FormView
):
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
        project = Project.objects.get(code=project_code,)
        membership = ProjectUserMembership.objects.create(
            project=project,
            user=self.request.user,
            date_joined=datetime.date.today(),
        )
        project_membership_created.delay(membership)
        return super().form_valid(form)


class ProjectUserRequestMembershipListView(
    PermissionAndLoginRequiredMixin, generic.ListView
):
    context_object_name = 'project_user_membership_requests'
    paginate_by = 50
    model = ProjectUserMembership
    template_name = 'project/membership/requests.html'
    ordering = ['-created_time']
    permission_required = 'project.add_project'

    def get_queryset(self):
        queryset = super().get_queryset()
        projects = Project.objects.filter(tech_lead=self.request.user,)
        queryset = queryset.filter(project__in=projects)
        # Omit the user's membership request
        return queryset.exclude(user=self.request.user)


class ProjectUserRequestMembershipUpdateView(
    LoginRequiredMixin, generic.UpdateView
):
    success_url = reverse_lazy('project-user-membership-request-list')
    context_object_name = 'project_user_membership_requests'
    model = ProjectUserMembership
    fields = ['status']
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
            condition = membership.is_owner_editable(
            ) and project.tech_lead == user
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
            try:
                update_openldap_project_membership(project_membership=form.instance)
            except:
                return JsonResponse({'message': 'We\'re sorry, something went wrong adding this use.'}, status=500)

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
        return queryset.filter(user=self.request.user)


class ProjectMembershipInviteView(
    PermissionRequiredMixin, SuccessMessageMixin, LoginRequiredMixin, FormView
):
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
        return reverse_lazy(
            'project-application-detail', args=[self.kwargs['pk']]
        )

    def project_passes_test(self, request):
        try:
            return Project.objects.filter(
                id=self.kwargs['pk'], tech_lead=self.request.user
            ).exists()
        except Exception:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.project_passes_test(request):
            return HttpResponseRedirect(
                reverse_lazy(
                    'project-application-detail', args=[self.kwargs['pk']]
                )
            )
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
            status=ProjectUserMembership.AUTHORISED,
        )
        return super().form_valid(form)
