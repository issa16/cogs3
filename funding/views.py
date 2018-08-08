from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from .forms import FundingSourceForm
from .forms import PublicationForm
from .models import FundingSource
from .models import Publication
from .models import Attribution

# Create your views here.


class FundingSourceCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = FundingSource
    success_url = reverse_lazy('list-attributions')
    success_message = _("Successfully added funding source.")
    template_name = 'funding/fundingsource_form.html'

    def get_form(self):
        return FundingSourceForm(
            self.request.user,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        fundingsource = form.save(commit=False)
        fundingsource.created_by = self.request.user
        fundingsource.save()
        if self.request.GET.get('_popup'):
            return HttpResponse('''
                Closing popup
                <script>
                opener.updateField(window);
                window.close();
                </script>
            ''')
        return HttpResponseRedirect(reverse_lazy('list-attributions'))


class PublicationCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = Publication
    success_url = reverse_lazy('list-attributions')
    success_message = _("Successfully added publication.")

    def get_form(self):
        return PublicationForm(
            self.request.user,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        publication = form.save(commit=False)
        publication.created_by = self.request.user
        publication.save()
        if self.request.GET.get('_popup'):
            return HttpResponse('''
                Closing popup
                <script>
                opener.updateField(window);
                window.close();
                </script>
            ''')
        return HttpResponseRedirect(reverse_lazy('list-attributions'))


class AttributionListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'attributions'
    template_name = 'funding/list.html'
    model = Attribution
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by=user)
        return queryset.order_by('-created_time')


class PublicationListView(AttributionListView):
    model = Publication


class FundingSourceListView(AttributionListView):
    model = FundingSource


class AttributionUpdateView(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = Attribution
    success_message = _("Successfully modified attribution.")
    success_url = reverse_lazy('list-attributions')

    def get_object(self, queryset=None):
        ''' Fetch the child object, not the attribution '''
        obj = super(generic.UpdateView, self).get_object(queryset=queryset)
        self.type = obj.type
        return obj.child

    def get_form(self):
        if self.type == 'fundingsource':
            return FundingSourceForm(
                self.request.user,
                **self.get_form_kwargs()
            )
        if self.type == 'publication':
            return PublicationForm(
                self.request.user,
                **self.get_form_kwargs()
            )

    def user_passes_test(self, request):
        return Attribution.objects.filter(id=self.kwargs['pk'], created_by=self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-attributions'))
        return super().dispatch(request, *args, **kwargs)


class AttributioneDeleteView(LoginRequiredMixin, generic.DeleteView):
    ''' Delete an attribution. This will also delete the child. '''
    model = Attribution
    success_message = _("Funding source deleted.")
    success_url = reverse_lazy('list-attributions')
    template_name = 'funding/delete.html'

    def user_passes_test(self, request):
        return FundingSource.objects.filter(id=self.kwargs['pk'], created_by=self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-attributions'))
        return super().dispatch(request, *args, **kwargs)
