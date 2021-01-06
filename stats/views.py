from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from project.mixins import PermissionAndLoginRequiredMixin
from project.models import Project
from system.models import Partition

from .parsers.project_stats_parser import ProjectStatsParser


def parse_date_range(request):
    '''
    Parse the query's start date if supplied.
    Otherwise, default to the date 12 months ago.
    '''
    start_date = request.GET.get('start_date', None)
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except Exception as e:
        print(e)
        start_date = date.today() + relativedelta(months=-12)
    '''
    Parse the query's end date if supplied.
    Otherwise, default to today's date.
    '''
    end_date = request.GET.get('end_date', None)
    try:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except Exception:
        end_date = date.today()
    return start_date, end_date


def parse_project_stats(context, request):
    '''
    Parse the compute and storage stats for given project
    over a valid date range.
    '''
    project = context['active_project']

    # Parse the date range
    start_date, end_date = parse_date_range(request)

    # Add to the context to maintain search range between request.
    context['query_start_date'] = start_date
    context['query_end_date'] = end_date

    # Create a ProjectStatsParser for the project
    stats_parser = ProjectStatsParser(
        project,
        start_date,
        end_date,
    )

    # Enable access via templates
    context['stats_parser'] = stats_parser

    # Retrieve core partitions stats in date range
    context['compute_stats_in_date_range'] = stats_parser.partition_stats_in_date_range(partition=Partition.CORE)

    # Retrieve core partitions stats to present
    context['compute_stats_to_present'] = stats_parser.partition_stats_in_date_range(
        start_date=datetime.now() - timedelta(days=365 * 10),
        partition=Partition.CORE,
    )

    # Retrieve researcher owned partitions stats in date range
    context['research_stats_in_date_range'] = stats_parser.partition_stats_in_date_range(partition=Partition.RESEARCH)

    # Retrieve researcher owned partitions stats to present
    context['research_stats_to_present'] = stats_parser.partition_stats_in_date_range(
        start_date=datetime.now() - timedelta(days=365 * 10),
        partition=Partition.RESEARCH,
    )

    # Retrieve storage stats
    context['storage_stats'] = stats_parser.storage_stats_in_date_range()

    return context


# DataAnalyticsPermissionMixin
class LatestProjectView(
    PermissionAndLoginRequiredMixin,
    TemplateView,
):
    template_name = 'stats/index.html'
    permission_required = 'project.change_project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_staff:
            '''
            A member of staff should have access to the data-analytics page.
            They should not be a techincal lead of a project, therefore
            available project codes and the latest project should be empty.
            '''
            context['project_codes'] = None
            context['active_project'] = None
        else:
            '''
            For technical leads of a project, we should return a list
            of their project codes and load the latest project they
            have created as the default active project to display.
            '''
            context['project_codes'] = ProjectStats.project_codes_for_tech_lead(user)
            context['active_project'] = Project.latest_project(user)
            context = parse_project_stats(context, self.request)
        return context


class ProjectDetailView(
    PermissionAndLoginRequiredMixin,
    TemplateView,
):
    '''
    The ProjectDetailView should return details of a project given a
    valid project code.
    '''
    context_object_name = 'projects'
    model = Project
    template_name = 'stats/index.html'
    permission_required = 'project.change_project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['project_codes'] = ProjectManager.project_codes_for_tech_lead(user)
        try:
            context['active_project'] = Project.objects.get(tech_lead=user, code=kwargs['code'])
            context = parse_project_stats(context, self.request)
        except Project.DoesNotExist:
            context['active_project'] = None
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProjectSearchView(
    PermissionAndLoginRequiredMixin,
    TemplateView,
):
    '''
    Members of staff can use the SCW administration form in the
    data-analytics page to view details on any project.
    '''
    context_object_name = 'projects'
    model = Project
    template_name = 'stats/index.html'
    permission_required = 'project.change_project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_codes'] = None
        context['active_project'] = None
        try:
            project_code = self.request.GET.get('code')
            context['active_project'] = Project.objects.get(code=project_code)
            context = parse_project_stats(context, self.request)
        except Project.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'Project does not exist.')
        return context


def ProjectStatsParserJSONView(request):
    data = {}
    if request.GET:
        try:
            # Determine user
            user = request.user

            # Find the project
            project_code = request.GET.get('code')
            if user.is_staff:
                # Staff can view all projects
                project = Project.objects.get(code=project_code)
            else:
                # Tech leads can only view their own projects
                project = Project.objects.get(
                    code=project_code,
                    tech_lead=user,
                )

            # Parse the date range
            start_date, end_date = parse_date_range(request)

            # Create a ProjectStatsParser for the project
            stats_parser = ProjectStatsParser(
                project,
                start_date,
                end_date,
            )

            # Overview stats
            data['pi_projects'] = stats_parser.pi_projects()
            data['user_status'] = stats_parser.user_status()

            # Compute stats
            data['rate_of_usage'] = stats_parser.rate_of_usage()
            data['cumlative_usage'] = stats_parser.cumlative_usage()
            data['individual_user_usage'] = stats_parser.individual_user_usage()
            data['usage_by_partition'] = stats_parser.usage_by_partition()
            data['efficency'] = stats_parser.efficency()
            data['num_jobs_per_month'] = stats_parser.num_jobs_per_month()
            data['per_job_avg_stats'] = stats_parser.per_job_avg_stats()
            data['core_count_node_utilisation'] = stats_parser.core_count_node_utilisation()

            # Storage stats
            data['disk_space'] = stats_parser.disk_space()
            data['file_count'] = stats_parser.file_count()

            # Return data dict as a json response
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse(data, safe=False)

    return JsonResponse(data, safe=False)
