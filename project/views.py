import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import FormView

from .forms import ProjectCreationForm
from .forms import ProjectUserMembershipCreationForm
from .models import Project
from .models import ProjectUserMembership


class ProjectCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    form_class = ProjectCreationForm
    success_url = reverse_lazy('project-application-list')
    success_message = "Successfully submitted a project application."
    template_name = 'project/create.html'

    def form_valid(self, form):
        form.instance.tech_lead = self.request.user
        return super().form_valid(form)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'projects'
    template_name = 'project/applications.html'
    model = Project
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(Q(tech_lead=user))
        return queryset.order_by('-created_time')


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = 'project'
    template_name = 'project/application_detail.html'
    model = Project

    def user_passes_test(self, request):
        try:
            project_id = self.kwargs['pk']
            user = self.request.user
            Project.objects.get(id=project_id, tech_lead=user)
        except Exception:
            return False
        else:
            return True

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('project-application-list'))
        return super().dispatch(request, *args, **kwargs)


class ProjectUserMembershipFormView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    form_class = ProjectUserMembershipCreationForm
    success_url = reverse_lazy('project-membership-list')
    success_message = "Successfully submitted a project membership request."
    template_name = 'project/membership/create.html'

    def get_initial(self):
        data = super().get_initial()
        data.update({'user': self.request.user})
        return data

    def form_valid(self, form):
        project_code = form.cleaned_data['project_code']
        ProjectUserMembership.objects.create(
            project=Project.objects.get(code=project_code, status=Project.APPROVED),
            user=self.request.user,
            date_joined=datetime.date.today(),
        )
        return super().form_valid(form)


class ProjectUserRequestMembershipListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    permission_required = 'project.change_projectusermembership'
    context_object_name = 'project_user_membership_requests'
    template_name = 'project/membership/requests.html'
    model = ProjectUserMembership
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        projects = Project.objects.filter(tech_lead=self.request.user, status=Project.APPROVED)
        queryset = queryset.filter(project__in=projects)
        queryset = queryset.exclude(user=self.request.user)  # Omit the user's own membership request
        return queryset.order_by('-created_time')


class ProjectUserRequestMembershipUpdateView(PermissionRequiredMixin, LoginRequiredMixin, generic.UpdateView):
    permission_required = 'project.change_projectusermembership'
    success_url = reverse_lazy('project-user-membership-request-list')
    context_object_name = 'project_user_membership_requests'
    model = ProjectUserMembership
    fields = ['status']

    def user_passes_test(self, request):
        # Ensure the project belongs to the user attempting to update the membership status
        try:
            project_id = request.POST.get('project_id')
            request_id = request.POST.get('request_id')
            user = self.request.user
            project = Project.objects.get(id=project_id, tech_lead=user)
            ProjectUserMembership.objects.get(id=request_id, project=project)
        except Exception:
            return False
        else:
            return True

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('project-user-membership-request-list'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {'message': 'Successfully updated.'}
            return JsonResponse(data)
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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        queryset = queryset.filter(project__status=Project.APPROVED)
        return queryset.order_by('-modified_time')
