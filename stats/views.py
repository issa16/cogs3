from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = 'stats/index.html'
