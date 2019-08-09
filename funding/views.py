from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from common.util import email_user

from .generate_docx import create_funding_document
from .forms import FundingSourceForm
from .forms import AddFundingSourceForm
from .forms import PublicationForm
from .forms import FundingSourceApprovalForm
from .models import FundingSource
from .models import Publication
from .models import Attribution
from .models import FundingSourceMembership
from institution.models import Institution


# Create your views here.


class FundingSourceCreateView(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    model = FundingSource
    form_class = FundingSourceForm
    success_url = reverse_lazy('list-attributions')
    success_message = _("Successfully added funding source.")
    template_name = 'funding/fundingsource_form.html'

    def notify_pi(self, fundingsource):
        user_name = fundingsource.created_by.first_name + ' ' + fundingsource.created_by.last_name
        subject = _('{company_name} Attribution Request by {user}'.format(company_name=settings.COMPANY_NAME, user=user_name))

        if fundingsource.pi.first_name:
            email_addressee = fundingsource.pi.first_name
            letter_from_line = ' '.join((fundingsource.pi.first_name,
                                         fundingsource.pi.last_name))
        else:
            email_addressee = fundingsource.pi.email.split('@')[0]
            letter_from_line = 'YOUR NAME HERE'

        context = {
            'first_name': email_addressee,
            'to': fundingsource.pi.email,
            'identifier': fundingsource.identifier,
            'title': fundingsource.title,
            'scw_email': fundingsource.pi.profile.institution.funding_document_email,
            'user': user_name,
        }
        docx_file = create_funding_document(
            fundingsource.funding_body.name,
            fundingsource.title,
            letter_from_line,
            fundingsource.pi.profile.shibbolethprofile.department,
            fundingsource.pi.profile.institution.funding_document_receiver,
            fundingsource.pi.profile.institution.funding_document_template,
        )
        email_user(
            subject,
            context,
            'notifications/funding/new_attribution.txt',
            'notifications/funding/new_attribution.html',
            attachments=[('letter_template.docx', docx_file)]
        )

    def get_form(self):
        kwargs = self.get_form_kwargs()
        if 'identifier' in self.kwargs:
            kwargs['initial']['identifier'] = self.kwargs['identifier']

        return FundingSourceForm(
            self.request.user,
            **kwargs
        )

    def form_valid(self, form):
        # If this is a popup, add the label to redirects
        if self.request.GET.get('_popup'):
            popup = "?_popup=1"
        else:
            popup = ""

        fundingsource = form.save(commit=False)
        domain = fundingsource.pi_email.split('@')[1]
        institution = Institution.objects.get(base_domain=domain)
        fundingsource.created_by = self.request.user
        fundingsource.save()

        if institution.needs_funding_approval:
            self.notify_pi(fundingsource)

        if self.request.GET.get('_popup'):
            return HttpResponse('''
                Closing popup
                <script>
                opener.updateField({new_id});
                window.close();
                </script>
            '''.format(new_id=fundingsource.id))
        return HttpResponseRedirect(reverse_lazy('list-attributions'))


class FundingSourceAddView(SuccessMessageMixin, LoginRequiredMixin, generic.FormView):
    ''' A customuser adds new fundingsources using this view. If a matching
        funding source is not found, the user is forwarded to the createview.
        If it is found, the user is added to its users list
    '''
    form_class = AddFundingSourceForm
    success_url = reverse_lazy('list-attributions')
    success_message = _("Successfully added funding source.")
    template_name = 'funding/fundingsource_form.html'

    def notify_pi(self, fundingsource, user_name):
        subject = _('{company_name} Attribution Request by {user}'.format(company_name=settings.COMPANY_NAME, user=user_name))
        context = {
            'first_name': fundingsource.pi.first_name,
            'to': fundingsource.pi.email,
            'identifier': fundingsource.identifier,
            'title': fundingsource.title,
            'user': user_name,
        }
        email_user(
            subject,
            context,
            'notifications/funding/attribution_request.txt',
            'notifications/funding/attribution_request.html',
        )

    def form_valid(self, form):
        # First time around we only ask for the identifier and check for matching funding sources
        identifier = form.cleaned_data['identifier']
        matching_funding_source = FundingSource.objects.filter(identifier=identifier)

        # If this is a popup, add the label to redirects
        if self.request.GET.get('_popup'):
            popup = "?_popup=1"
        else:
            popup = ""

        if matching_funding_source.exists():
            fundingsource = matching_funding_source.first()
            if fundingsource.pi.profile.institution.needs_funding_approval:
                user_is_member = FundingSourceMembership.objects.filter(
                    user=self.request.user,
                    fundingsource=fundingsource).exists()

                if user_is_member:
                    messages.add_message(self.request, messages.INFO,
                        "You already are a member of this funding source. It will become visible in attributions once the PI approves your membership")
                    return HttpResponseRedirect(reverse_lazy('list-attributions')+popup)
                else:
                    messages.add_message(
                        self.request, messages.INFO,
                        "A funding source with this identifier has been found "
                        "on the system. "
                        "An email has been sent to the PI provided " +
                        (f"({fundingsource.pi_email}) "
                         if fundingsource.pi_email
                         else '') +
                        "to request that you "
                        "are added to this funding. "
                    )

                    user_name = self.request.user.first_name + ' ' + self.request.user.last_name
                    self.notify_pi(fundingsource, user_name)
                    FundingSourceMembership.objects.get_or_create(
                        user=self.request.user,
                        fundingsource=fundingsource,
                        defaults={'approved': False}
                    )

                    return HttpResponseRedirect(reverse_lazy('list-attributions')+popup)

            else:
                if self.request.GET.get('_popup'):
                    return HttpResponse('''
                    Closing popup
                    <script>
                    opener.updateField({new_id});
                    window.close();
                    </script>
                    '''.format(new_id=fundingsource.id))
                return HttpResponseRedirect(reverse_lazy('list-attributions'))

        else:
            # No match, ask to create
            messages.add_message(self.request, messages.INFO,
                    "You have requested to attribute a funding source that does not yet exist in the system. "
                    "Please include additional detail for our records.")
            if identifier:
                endpoint = reverse_lazy('create-funding-source-with-identifier', args=[identifier])
            else:
                # this code is currently inaccessible due to validation on
                # identfier in FundingSource, but redirecting in case of identifier
                # somehow not being truthy
                endpoint = reverse_lazy('create-funding-source')

            return HttpResponseRedirect(endpoint + popup)

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
                opener.updateField({new_id});
                window.close();
                </script>
            '''.format(new_id=publication.id))
        return HttpResponseRedirect(reverse_lazy('list-attributions'))


class AttributionListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'attributions'
    template_name = 'funding/list.html'
    model = Attribution
    paginate_by = 10
    model_filter = None

    def get_queryset(self):
        user = self.request.user
        query_filter = {}
        if self.model_filter:
            query_filter[f'{self.model_filter}__isnull'] = False
        queryset = super().get_queryset().filter(**query_filter)
        owned_set = queryset.filter(owner=user)
        user_set = queryset.filter(fundingsource__in=FundingSource.objects.filter(
            fundingsourcemembership__user=user,
            fundingsourcemembership__approved=True,
        ))
        return (owned_set | user_set).order_by('-created_time')


class PublicationListView(AttributionListView):
    model_filter = 'publication'


class FundingSourceListView(AttributionListView):
    model_filter = 'fundingsource'


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
        return (
            Attribution.objects.filter(id=self.kwargs['pk'],
                                       owner=self.request.user).exists()
            or self.request.user.has_perm('funding.approve_funding_sources')
        )

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # User cannot update a funding source if the funding approval workflow is required
        if obj.type == 'fundingsource' and obj.pi.profile.institution.needs_funding_approval:
            if not self.request.user.has_perm('funding.approve_funding_sources'):
                return HttpResponseRedirect(reverse('funding_source-detail-view',kwargs={'pk':obj.id}))

        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-attributions'))
        return super().dispatch(request, *args, **kwargs)


class FundingsourceDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = 'grant'
    model = FundingSource

    def user_passes_test(self, request):
        return FundingSourceMembership.objects.filter(
            fundingsource=FundingSource.objects.get(id=self.kwargs['pk']),
            user=self.request.user
        ).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-attributions'))
        return super().dispatch(request, *args, **kwargs)


class AttributionDeleteView(LoginRequiredMixin, generic.DeleteView):
    ''' Delete an attribution. This will also delete the child. '''
    model = Attribution
    success_message = _("Funding source deleted.")
    success_url = reverse_lazy('list-attributions')
    template_name = 'funding/delete.html'

    def user_passes_test(self, request):
        attribution = self.get_object()
        if attribution.is_fundingsource:
            fundingsource = attribution.child
            if (
                    fundingsource.approved and
                    fundingsource.pi.profile.institution.needs_funding_approval
            ):
                return False
            else:
                return fundingsource.owner == self.request.user
        return Attribution.objects.filter(id=self.kwargs['pk'], owner=self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            return HttpResponseRedirect(reverse('list-attributions'))
        return super().dispatch(request, *args, **kwargs)


class ListFundingSourceMembership(LoginRequiredMixin, generic.ListView):
    # List funding source memberships the user is the PI in and can approve users
    context_object_name = 'memberships'
    template_name = 'funding/memberships.html'
    model = FundingSourceMembership
    paginate_by = 10
    ordering = ['-created_time']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(fundingsource__pi=user)
        return queryset


class ToggleFundingSourceMembershipApproved(LoginRequiredMixin, generic.UpdateView):
    context_object_name = 'memberships'
    model = FundingSourceMembership
    fields = ['approved']

    def request_allowed(self, request):
        try:
            membership_id = self.kwargs['pk']
            membership = FundingSourceMembership.objects.get(id=membership_id)
            condition = membership.fundingsource.pi == request.user
            return condition
        except Exception:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.request_allowed(request):
            return HttpResponseRedirect(reverse('list-funding_source_memberships'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = HttpResponseRedirect(reverse('list-funding_source_memberships'))
        membership = FundingSourceMembership.objects.get(id=self.kwargs['pk'])
        if membership.approved:
            membership.approved = False
        else:
            membership.approved = True
        membership.save()

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


class ListUnapprovedFundingSources(PermissionRequiredMixin, generic.ListView):
    # List unnapproved fundingsources for approval by a user with permissions

    context_object_name = 'fundingsources'
    template_name = 'funding/approvefundingsources.html'
    permission_required = 'funding.approve_funding_sources'
    raise_exception = True
    model = FundingSource
    paginate_by = 10
    ordering = ['-created_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(approved=False)
        return queryset


class ApproveFundingSource(SuccessMessageMixin, PermissionRequiredMixin, generic.UpdateView):
    model = FundingSource
    form_class = FundingSourceApprovalForm
    success_message = _("Successfully approved funding source.")
    success_url = reverse_lazy('list-unapproved-funding_sources')
    template_name = 'funding/fundingsource_approval_form.html'
    permission_required = 'funding.approve_funding_sources'
    raise_exception = True
