from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from project.models import ProjectUserMembership, Project
from users.models import Profile


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if self.request.user.has_perm('project.change_projectusermembership'):
            num_requests = ProjectUserMembership.objects.awaiting_authorisation(self.request.user).count()
            context['project_user_requests_count'] = num_requests

        if self.request.user.has_perm('project.add_project'):
            num_requests = Project.objects.filter(tech_lead=self.request.user, status=Project.AWAITING_APPROVAL).count()
            context['project_application_count'] = num_requests

        if self.request.user.profile.account_status == Profile.AWAITING_APPROVAL:
            context['account_status_message'] = _(
                'Your account is currently being configured. You should receive an email shortly '
                'with instructions on how to access the compute cluster.')

        return context
