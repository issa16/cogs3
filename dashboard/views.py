from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from project.models import ProjectUserMembership
from users.models import Profile


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if self.request.user.has_perm('project.change_projectusermembership'):
            num_requests = ProjectUserMembership.objects.awaiting_authorisation(self.request.user).count()
            context['project_user_requests_count'] = num_requests

        return context
