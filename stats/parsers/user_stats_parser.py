from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from project.models import Project, ProjectUserMembership
from stats.models import ComputeDaily

from .util import parse_efficency_result_set, seconds_to_hours


class UserStatsParser:
    '''
    User stats parser.
    '''

    def __init__(self, user, project_filter):
        self.user = user
        self.project_ids = self._parse_project_ids(user, project_filter)
        # Default to last 12 months
        self.start_date = date.today() + relativedelta(months=-12)
        self.end_date = date.today()

    def rate_of_usage_per_month(self):
        '''
        Return the rate of usage grouped by month.
        '''
        try:
            # Query rate of usage
            result = ComputeDaily.objects.filter(
                project__in=self.project_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                wait_time=Sum('wait_time'),
                cpu_time=Sum('cpu_time'),
                wall_time=Sum('wall_time'),
            ).order_by('month')

            # Parse result
            dates = []
            wait_time = []
            cpu_time = []
            wall_time = []
            for row in result:
                dates.append(row['month'].strftime('%b %Y'))
                wait_time.append(seconds_to_hours(row['wait_time'].total_seconds()))
                cpu_time.append(seconds_to_hours(row['cpu_time'].total_seconds()))
                wall_time.append(seconds_to_hours(row['wall_time'].total_seconds()))

            # Build response
            data = {
                'dates': dates,
                'wait_time': wait_time,
                'cpu_time': cpu_time,
                'wall_time': wall_time,
            }
        except Exception:
            data = {}
        return data

    def cumlative_total_usage_per_month(self):
        '''
        Return the cumlative total usage grouped by month.
        '''
        try:
            # Query cumlative total usage
            result = ComputeDaily.objects.filter(
                project__in=self.project_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                wait_time=Sum('wait_time'),
                cpu_time=Sum('cpu_time'),
                wall_time=Sum('wall_time'),
            ).order_by('month')

            # Init response lists
            dates = [result[0]['month'].strftime('%b %Y')]
            wait_time = [seconds_to_hours(result[0]['wait_time'].total_seconds())]
            cpu_time = [seconds_to_hours(result[0]['cpu_time'].total_seconds())]
            wall_time = [seconds_to_hours(result[0]['wall_time'].total_seconds())]

            # Build cumlative values
            if len(result) > 1:
                for row in result[1:]:
                    dates.append(row['month'].strftime('%b %Y'))
                    wait_time.append(seconds_to_hours(row['wait_time'].total_seconds()) + wait_time[-1])
                    cpu_time.append(seconds_to_hours(row['cpu_time'].total_seconds()) + cpu_time[-1])
                    wall_time.append(seconds_to_hours(row['wall_time'].total_seconds()) + wall_time[-1])

            # Build response
            data = {
                'dates': dates,
                'wait_time': wait_time,
                'cpu_time': cpu_time,
                'wall_time': wall_time,
            }
        except Exception:
            data = {}
        return data

    def efficency_per_month(self):
        '''
        Return the efficency grouped by month.
        '''
        try:
            # Query cpu and wall time in date range
            results_in_date_range = ComputeDaily.objects.filter(
                project__in=self.project_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                cpu_time_sum=Sum('cpu_time'),
                wall_time_sum=Sum('wall_time'),
            ).order_by('month')

            # Parse in date range results
            dates = [row['month'].strftime('%b %Y') for row in results_in_date_range]
            efficency = parse_efficency_result_set(results_in_date_range)

            # Build response
            data = {
                'dates': dates,
                'efficency': efficency,
            }
        except Exception:
            data = {}
        return data

    def num_jobs_per_month(self):
        '''
        Return the number of jobs grouped by month.
        '''
        try:
            # Query number of jobs in date range
            results_in_date_range = ComputeDaily.objects.filter(
                project__in=self.project_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                number_jobs=Sum('number_jobs'),
            ).order_by('month')

            # Parse in date range results
            dates = []
            number_jobs = []
            for row in results_in_date_range:
                dates.append(row['month'].strftime('%b %Y'))
                number_jobs.append(row['number_jobs'])

            # Build response
            data = {
                'dates': dates,
                'number_jobs': number_jobs,
            }
        except Exception:
            data = {}
        return data

    def _parse_project_ids(self, user, project_filter):
        '''
        Return project ids from a given list of project codes.
        '''
        project_ids = []

        # Validate the user has a project user membership to the project codes.
        valid_projects = ProjectUserMembership.objects.filter(
            user=self.user,
            status=ProjectUserMembership.AUTHORISED,
        ).values('project__code', 'project__id')

        if valid_projects:
            # Return the project id's for all valid project codes.
            if project_filter == 'all':
                project_ids = [project['project__id'] for project in valid_projects]
            else:
                # Return the project id of the chosen project code.
                try:
                    # Check the project code provided is in valid projects.
                    valid = False
                    for project in valid_projects:
                        if project['project__code'] == project_filter:
                            valid = True
                            break
                    if valid:
                        project = Project.objects.get(code=project_filter)
                        project_ids = [project.id]
                except Exception:
                    # A user is most likely trying to access a project
                    # in which they do not have a project user membership.
                    pass
        return project_ids
