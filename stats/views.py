from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from project.mixins import PermissionAndLoginRequiredMixin
from project.models import Project
from system.models import Partition
from weasyprint import HTML

from .parsers.project_stats_parser import ProjectStatsParser
from .parsers.user_stats_parser import UserStatsParser


class IndexView(
    PermissionAndLoginRequiredMixin,
    TemplateView,
):
    '''
    IndexView
    '''
    template_name = 'stats/index.html'
    permission_required = 'project.change_project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            # Which projects is this user a technical lead of?
            projects = Project.objects.filter(tech_lead=user).order_by('-start_date')
            context['project_codes'] = [project.code for project in projects]

            # Parse the date range.
            start_date, end_date = parse_date_range(self.request)

            # Add to the context to maintain search range between requests.
            context['query_start_date'] = start_date
            context['query_end_date'] = end_date

            # Parse the project within the query params and verify.
            project_code = self.request.GET.get('code', '')

            if user.is_staff:
                # Staff have the ability to query any project stats data.
                selected_project = Project.objects.get(code=project_code)
            else:
                # Verify non staff member is the tech lead of the project.
                selected_project = Project.objects.get(
                    code=project_code,
                    tech_lead=user,
                )

            context['selected_project'] = selected_project

            # Query the relevant data from the stats tables.
            stats_parser = ProjectStatsParser(
                selected_project,
                'all',
                start_date,
                end_date,
            )

            # Build project stats and add to request context.
            context = build_project_stats(stats_parser, context)
        except Exception:
            if user.is_staff and project_code:
                messages.add_message(self.request, messages.ERROR, 'Project does not exist.')
        return context


def parse_date_range(request):
    '''
    Parse the query's start date if supplied.
    Otherwise, default to the date 12 months ago.
    '''
    start_date = request.GET.get('start_date', None)
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except Exception:
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


def build_project_stats(stats_parser, data):
    # Retrieve project overview stats
    data['total_core_hours'] = stats_parser.total_core_hours()
    data['total_cpu_hours'] = stats_parser.total_cpu_hours()
    data['total_slurm_jobs'] = stats_parser.total_slurm_jobs()
    data['efficiency'] = stats_parser.efficiency()

    # Retrieve core partitions stats in date range
    data['core_partitions_in_date_range'] = stats_parser.partition_stats_in_date_range(
        partition_type=[
            Partition.CORE,
        ]
    )

    # Retrieve core partitions stats to present
    data['core_partitions_to_present'] = stats_parser.partition_stats_in_date_range(
        start_date=stats_parser.project.start_date,
        partition_type=[
            Partition.CORE,
        ],
    )

    # Retrieve researcher funded partitions stats in date range
    data['researcher_partitions_in_date_range'] = stats_parser.partition_stats_in_date_range(
        partition_type=[
            Partition.RESEARCH,
        ],
    )

    # Retrieve researcher funded partitions stats to present
    data['researcher_partitions_to_present'] = stats_parser.partition_stats_in_date_range(
        start_date=stats_parser.project.start_date,
        partition_type=[
            Partition.RESEARCH,
        ],
    )

    # Retrieve compute totals in date range
    data['compute_totals_in_date_range'] = stats_parser.partition_stats_in_date_range(
        partition_type=[
            Partition.CORE,
            Partition.RESEARCH,
        ],
    )

    # Retrieve compute totals to present
    data['compute_totals_to_present'] = stats_parser.partition_stats_in_date_range(
        start_date=stats_parser.project.start_date,
        partition_type=[
            Partition.CORE,
            Partition.RESEARCH,
        ],
    )

    # Retrieve list of partitions used
    data['core_partitions_used'] = stats_parser.partitions_used(partition_type=Partition.CORE)
    data['researcher_partitions_used'] = stats_parser.partitions_used(partition_type=Partition.RESEARCH)

    # Retrieve storage stats
    data['storage_stats'] = stats_parser.storage_stats_in_date_range()

    return data


def UserStatsParserJSONView(request):
    '''
    UserStatsParserJSONView
    '''
    data = {}
    if request.GET:
        try:
            # Determine user
            user = request.user

            # Find the project
            project_filter = request.GET.get('code')

            # Create a UserStatsParser for the project
            stats_parser = UserStatsParser(
                user=user,
                project_filter=project_filter,
            )

            # Query stats
            data['rate_of_usage_per_month'] = stats_parser.rate_of_usage_per_month()
            data['cumlative_total_usage_per_month'] = stats_parser.cumlative_total_usage_per_month()
            data['efficiency_per_month'] = stats_parser.efficiency_per_month()
            data['num_jobs_per_month'] = stats_parser.num_jobs_per_month()

        except Exception:
            pass

    return JsonResponse(data, safe=False)


def ProjectStatsParserJSONView(request):
    '''
    ProjectStatsParserJSONView
    '''
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

            # Parse partition id
            partition_filter = request.GET.get('partition')
            if not partition_filter:
                partition_filter = 'all'

            # Parse the date range
            start_date, end_date = parse_date_range(request)

            # Create a ProjectStatsParser for the project
            stats_parser = ProjectStatsParser(
                project,
                partition_filter,
                start_date,
                end_date,
            )

            # Overview stats
            data['pi_projects'] = stats_parser.pi_projects()
            data['user_status'] = stats_parser.user_status()
            data['efficiency'] = stats_parser.efficiency()

            # Compute stats
            data['rate_of_usage'] = stats_parser.rate_of_usage()
            data['cumlative_total_usage'] = stats_parser.cumlative_total_usage()
            data['top_users_usage'] = stats_parser.top_users_usage()
            data['usage_by_partition'] = stats_parser.usage_by_partition()
            data['efficiency_per_month'] = stats_parser.efficiency_per_month()
            data['num_jobs_per_month'] = stats_parser.num_jobs_per_month()
            data['per_job_avg_stats'] = stats_parser.per_job_avg_stats()
            data['core_count_node_utilisation'] = stats_parser.core_count_node_utilisation()

            # Storage stats
            data['disk_space'] = stats_parser.disk_space()
            data['file_count'] = stats_parser.file_count()

        except Exception:
            pass

    return JsonResponse(data, safe=False)


def GeneratePDF(request):
    '''
    GeneratePDF
    '''
    if request.GET:
        try:
            # Determine user
            user = request.user

            # Parse query params
            project_code = request.GET.get('code')
            start_date, end_date = parse_date_range(request)
            partition_filter = request.GET.get('partition', 'all')

            if user.is_staff:
                # Staff can view all projects
                project = Project.objects.get(code=project_code)
            else:
                # Tech leads can only view their own projects
                project = Project.objects.get(
                    code=project_code,
                    tech_lead=user,
                )

            # Create a ProjectStatsParser for the project
            stats_parser = ProjectStatsParser(
                project,
                partition_filter,
                start_date,
                end_date,
            )

            context = {
                'project': project,
                'query_start_date': start_date,
                'query_end_date': end_date,
                'user': user,
            }
            context = build_project_stats(stats_parser, context)

            html_string = render_to_string('stats/pdf_template.html', context)
            html = HTML(string=html_string, base_url=request.build_absolute_uri())
            html.write_pdf(target='/tmp/mypdf.pdf')

            fs = FileSystemStorage('/tmp')
            with fs.open('mypdf.pdf') as pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="' + project.code + '".pdf"'
            return response
        except Exception:
            pass
    return HttpResponse()
