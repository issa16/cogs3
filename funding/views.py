from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect

from .forms import FundingSourceForm
from .models import FundingSource

# Create your views here.


class FundingSourceCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = FundingSource
    success_url = reverse_lazy('list-funding-sources')
    success_message = _("Successfully added funding source.")
    template_name = 'funding/create.html'

    def get_form(self):
        return FundingSourceForm(
            self.request.user,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        fundingsource = form.save(commit=False)
        fundingsource.created_by = self.request.user
        fundingsource.save()
        return HttpResponseRedirect(reverse_lazy('list-funding-sources'))


class FundingSourceListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'sources'
    template_name = 'funding/list.html'
    model = FundingSource
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by=user)
        return queryset.order_by('-created_time')


class FundingSourceUpdateView(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = FundingSource
    success_message = _("Successfully modified funding source.")
    success_url = reverse_lazy('list-funding-sources')
    template_name = 'funding/create.html'

    def get_form(self):
        return FundingSourceForm(
            self.request.user,
            **self.get_form_kwargs()
        )

    def user_passes_test(self, request):
        return FundingSource.objects.filter(id=self.kwargs['pk'], created_by=self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-funding-sources'))
        return super().dispatch(request, *args, **kwargs)


class FundingSourceDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = FundingSource
    success_message = _("Funding source deleted.")
    success_url = reverse_lazy('list-funding-sources')
    template_name = 'funding/delete.html'

    def user_passes_test(self, request):
        return FundingSource.objects.filter(id=self.kwargs['pk'], created_by=self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-funding-sources'))
        return super().dispatch(request, *args, **kwargs)
