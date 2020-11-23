from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = 'stats/index.html'


class ProjectDataView(LoginRequiredMixin, TemplateView):
    template_name = 'stats/project_data.html'


class ComputeConsumptionDataView(LoginRequiredMixin, TemplateView):
    template_name = 'stats/compute_consumption_data.html'


class StorageConsumptionDataView(LoginRequiredMixin, TemplateView):
    template_name = 'stats/storage_consumption_data.html'
