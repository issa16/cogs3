from django.views.generic import TemplateView

from project.models import Project
from project.models import Project
from project.models import ProjectUserMembership


class DashboardView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # How many user membership requests are awaiting authorisation?
            projects = Project.objects.filter(tech_lead=self.request.user)
            project_user_memberships = ProjectUserMembership.objects.filter(
                project__in=projects,
                status=ProjectUserMembership.AWAITING_AUTHORISATION,
            )
            context['project_user_requests_count'] = project_user_memberships.count()
        return context
