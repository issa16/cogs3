from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from project.models import ProjectUserMembership


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if self.request.user.has_perm('project.change_projectusermembership'):
            # How many project user membership requests are awaiting authorisation?
            num_requests = ProjectUserMembership.objects.awaiting_authorisation(self.request.user).count()
            context['project_user_requests_count'] = num_requests

        return context
