import datetime
from statistics import mean

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncMonth
from project.models import Project, ProjectUserMembership
from stats.models import ComputeDaily, StorageWeekly
from system.models import Partition

from .util import kb_to_gb, parse_efficiency_result_set, seconds_to_hours


class ProjectStatsParser:
    '''
    Project stats parser.
    '''

    def __init__(
        self,
        project,
        partition_filter,
        start_date,
        end_date,
    ):
        self.project = project
        self.partition_ids = self._parse_partition_ids(partition_filter)
        self.start_date = start_date
        self.end_date = end_date + datetime.timedelta(days=1)

    def _parse_project_statuses(self, projects):
        '''
        Given a list of projects, parse the projects statuses into
        a dict.
        '''
        # Define date range for active and inactive query
        n_months = 6
        date_start = datetime.date.today() + relativedelta(months=-n_months)
        date_end = datetime.date.today()
        data = {
            'Active': 0,
            'Dormant': 0,
            'Inactive': 0,
            'Retired': 0,
        }
        for project in projects:
            # Dormant projects - defined by never running a job
            # (i.e. no entires in ComputeDaily table)
            if not ComputeDaily.objects.filter(project=project).exists():
                data['Dormant'] += 1
                continue

            # Active projects - defined by running a job within the
            # last n_months
            # Inactive projects - defined by not running a job over
            # the last n_months
            active = ComputeDaily.objects.filter(
                project=project,
                date__range=[date_start, date_end],
            ).exists()
            if active:
                data['Active'] += 1
            else:
                data['Inactive'] += 1

            # Retired projects - defined by project state = closed
            if project.status == Project.CLOSED:
                data['Retired'] += 1
        return data

    def pi_projects(self):
        '''
        Return the number of active, dormant, inactive and retired projects
        for the project's principal investigator (PI).
        '''
        try:
            pi_email = self.project.pi_email
            if pi_email:
                # Find all projects that belong to a PI
                projects = Project.objects.filter(pi_email=pi_email)
            else:
                # No match found, use current project
                projects = self.project
            project_statuses = self._parse_project_statuses(projects)

            # Build response
            data = [
                ['Active', project_statuses['Active']],
                ['Dormant', project_statuses['Dormant']],
                ['Inactive', project_statuses['Inactive']],
                ['Retired', project_statuses['Retired']],
            ]
        except Exception:
            data = []
        return data

    def user_status(self):
        '''
        Return the number of active, dormant and inactive users.
        '''
        try:
            # Define date range
            n_months = 6
            date_start = datetime.date.today() + relativedelta(months=-n_months)
            date_end = datetime.date.today()

            # Active users - Defined by current project membership active
            active_users = ProjectUserMembership.objects.filter(
                project=self.project,
                status=ProjectUserMembership.AUTHORISED,
            )
            active_users_count = 0

            # Dormant users - Defined by current project membership active but
            # no usage for X months.
            dormant_users_count = 0
            for active_user in active_users:
                # Check ComputeDaily table for recent activity
                active = ComputeDaily.objects.filter(
                    project=self.project,
                    user=active_user.user,
                    date__range=[date_start, date_end],
                ).exists()
                if active:
                    active_users_count += 1
                else:
                    dormant_users_count += 1

            # Inactive users - Defined by current project membership revoked or
            # suspended.
            inactive_users_count = ProjectUserMembership.objects.filter(
                Q(status=ProjectUserMembership.REVOKED) | Q(status=ProjectUserMembership.SUSPENDED),
                project=self.project,
            ).count()

            # Build response
            data = [
                ['Active', active_users_count],
                ['Dormant', dormant_users_count],
                ['Inactive', inactive_users_count],
            ]
        except Exception:
            data = []
        return data

    def storage_stats_in_date_range(
        self,
        start_date=None,
        end_date=None,
    ):
        '''
        Return disk space and file count stats for a given date range.
        '''
        # Use dates stored in instance if not supplied via params.
        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date
        else:
            end_date = end_date + datetime.timedelta(days=1)

        data = {
            'home_space_used_avg': 0,
            'scratch_space_used_avg': 0,
            'home_files_used_avg': 0,
            'scratch_files_used_avg': 0,
        }

        # Calculate average disk space usage per week
        try:
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[start_date, end_date],
            ).aggregate(
                Avg('home_space_used'),
                Avg('scratch_space_used'),
            )
            data['home_space_used_avg'] = kb_to_gb(result['home_space_used__avg'])
            data['scratch_space_used_avg'] = kb_to_gb(result['scratch_space_used__avg'])
        except Exception:
            pass

        # Calculate average file count per week
        try:
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[start_date, end_date],
            ).aggregate(
                Avg('home_files_used'),
                Avg('scratch_files_used'),
            )
            data['home_files_used_avg'] = result['home_files_used__avg']
            data['scratch_files_used_avg'] = result['scratch_files_used__avg']
        except Exception:
            pass
        return data

    def disk_space(self):
        '''
        Return disk space usage for a date range (grouped by month).
        '''
        try:
            # Query disk space usage
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                home_space_used_sum=Sum('home_space_used'),
                scratch_space_used_sum=Sum('scratch_space_used'),
            ).order_by('month')

            # Parse results
            dates = []
            home = []
            scratch = []
            total = []
            for row in result:
                dates.append(row['month'].strftime('%b %Y'))
                home.append(kb_to_gb(row['home_space_used_sum']))
                scratch.append(kb_to_gb(row['scratch_space_used_sum']))
                total.append(kb_to_gb(row['home_space_used_sum'] + row['scratch_space_used_sum']))

            # Build response
            data = {
                'dates': dates,
                'home': home,
                'scratch': scratch,
                'total': total,
            }
        except Exception:
            data = {}
        return data

    def file_count(self):
        '''
        Return file count usage for a date range (grouped by month).
        '''
        try:
            # Query file count usage
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                home_files_used_sum=Sum('home_files_used'),
                scratch_files_used_sum=Sum('scratch_files_used'),
            ).order_by('month')

            # Parse result
            dates = []
            home = []
            scratch = []
            total = []
            for row in result:
                dates.append(row['month'].strftime('%b %Y'))
                home.append(row['home_files_used_sum'])
                scratch.append(row['scratch_files_used_sum'])
                total.append(row['home_files_used_sum'] + row['scratch_files_used_sum'])

            # Build response
            data = {
                'dates': dates,
                'home': home,
                'scratch': scratch,
                'total': total,
            }
        except Exception:
            data = {}
        return data

    def partitions_used(self, partition_type=Partition.CORE):
        '''
        Return a list of partitions used within date range.
        '''
        partition_names = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type=partition_type,
            date__range=[self.start_date, self.end_date],
        ).values('partition__id', 'partition__description').distinct()
        return partition_names

    def _parse_partition_ids(self, partition_filter):
        if partition_filter == 'all':
            ids = Partition.objects.all().values_list(
                'id',
                flat=True,
            )
        elif partition_filter == 'core':
            ids = Partition.objects.filter(partition_type=Partition.CORE).values_list(
                'id',
                flat=True,
            )
        elif partition_filter == 'research':
            ids = Partition.objects.filter(partition_type=Partition.RESEARCH).values_list(
                'id',
                flat=True,
            )
        else:
            # Ensure id is valid
            try:
                valid_partition = Partition.objects.filter(id=partition_filter).exists()
                if valid_partition:
                    ids = [partition_filter]
            except Exception:
                # Invalid id, default to showing all partitions
                ids = Partition.objects.all().values_list(
                    'id',
                    flat=True,
                )
        return ids

    def rate_of_usage(self):
        '''
        Return the rate of usage for a date range (grouped by month).
        '''
        try:
            # Query rate of usage
            result = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
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

    def cumulative_total_usage(self):
        '''
        Return the cumulative total usage for a date range (grouped by month).
        '''
        try:
            # Query cumulative total usage
            result = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
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

            # Build cumulative values
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

    def top_users_usage(self):
        '''
        Return top users usage for a date range.
        '''
        n_users = 10
        try:
            # Query top n users usage
            result = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(Count('user', distinct=True)).values('user__first_name', 'user__last_name').annotate(
                c=Count('id'),
                wall_time=Sum('wall_time'),
            ).order_by('-wall_time')[:n_users]

            # Parse result
            usernames = []
            wall_time = []
            for row in result:
                usernames.append(f"{row['user__first_name'].title()} {row['user__last_name'].title()}")
                wall_time.append(seconds_to_hours(row['wall_time'].total_seconds()))

            # Build response
            data = {
                'usernames': usernames,
                'wall_time': wall_time,
            }
        except Exception:
            data = {}
        return data

    def usage_by_partition(self):
        '''
        Return partition usage for a date range.
        '''
        try:
            # Query partition usage in date range
            results = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
                date__range=[self.start_date, self.end_date],
            ).values('partition__name').annotate(
                c=Count('id'),
                wall_time_sum=Sum('wall_time'),
            )

            # Calculate total wall time
            total_wall_time = sum([seconds_to_hours(row['wall_time_sum'].total_seconds()) for row in results])

            # Calculate percentages for each partition
            parition_names = []
            partition_percentages = []
            for row in results:
                parition_names.append(row['partition__name'])
                wall_time_sum = seconds_to_hours(row['wall_time_sum'].total_seconds())
                partition_percentages.append(round((wall_time_sum / total_wall_time) * 100, 2))

            # Build response
            data = {
                'parition_names': parition_names,
                'partition_percentages': partition_percentages,
            }
            return data
        except Exception:
            data = []
        return data

    def efficiency_per_month(self):
        '''
        Return the efficiency for a date range.
        '''
        try:
            # Query cpu and wall time in date range
            results_in_date_range = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                cpu_time_sum=Sum('cpu_time'),
                wall_time_sum=Sum('wall_time'),
            ).order_by('month')

            # Parse in date range results
            data = {}
            if results_in_date_range:
                dates, efficiency = parse_efficiency_result_set(results_in_date_range)
                data['dates'] = dates
                data['efficiency'] = efficiency
                data['avg_efficiency_in_date_range'] = round(sum(efficiency) / len(efficiency), 2)

            # Query cpu and wall time to present
            results_to_present = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                cpu_time_sum=Sum('cpu_time'),
                wall_time_sum=Sum('wall_time'),
            ).order_by('month')

            # Parse to present results
            if results_to_present:
                __, efficiency_to_present = parse_efficiency_result_set(results_to_present)
                avg_efficiency_to_present = round(sum(efficiency_to_present) / len(efficiency_to_present), 2)
                data['avg_efficiency_to_present'] = avg_efficiency_to_present
        except Exception:
            data = {}
        return data

    def num_jobs_per_month(self):
        '''
        Return the number of jobs for a date range.
        '''
        try:
            # Query number of jobs in date range
            results_in_date_range = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
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
            number_jobs_in_date_range = sum(number_jobs)

            # Query number of jobs to present
            number_jobs_to_present = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
            ).aggregate(number_jobs_sum=Sum('number_jobs'))['number_jobs_sum']

            # Build response
            data = {
                'dates': dates,
                'number_jobs': number_jobs,
                'number_jobs_in_date_range': number_jobs_in_date_range,
                'number_jobs_to_present': number_jobs_to_present,
            }
        except Exception:
            data = {}
        return data

    def _parse_per_job_avg_result_set(self, result_set):
        '''
        Return cpu time, wait time and wall time for a
        given result_set.
        '''
        cpu_time = []
        wait_time = []
        wall_time = []
        for row in result_set:
            cpu_time.append(round(seconds_to_hours(row['cpu_time'].total_seconds()) / row['number_jobs'], 2))
            wait_time.append(round(seconds_to_hours(row['wait_time'].total_seconds()) / row['number_jobs'], 2))
            wall_time.append(round(seconds_to_hours(row['wall_time'].total_seconds()) / row['number_jobs'], 2))
        return cpu_time, wait_time, wall_time

    def per_job_avg_stats(self):
        '''
        Return the per-job average CPU, Wait and Wall time for a date range.
        '''
        try:
            # Query per-job avg stats in date range
            results_in_date_range = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                cpu_time=Sum('cpu_time'),
                wait_time=Sum('wait_time'),
                wall_time=Sum('wall_time'),
                number_jobs=Sum('number_jobs')
            ).order_by('month')

            # Parse in date range results
            data = {}
            if results_in_date_range:
                data['dates'] = [row['month'].strftime('%b %Y') for row in results_in_date_range]
                cpu_time, wait_time, wall_time = self._parse_per_job_avg_result_set(results_in_date_range)
                data['cpu_time'] = cpu_time
                data['wait_time'] = wait_time
                data['wall_time'] = wall_time
                data['avg_cpu_time_in_date_range'] = round(mean(cpu_time), 2)
                data['avg_wait_time_in_date_range'] = round(mean(wait_time), 2)
                data['avg_wall_time_in_date_range'] = round(mean(wall_time), 2)

            # Query per-job avg stats to present
            results_to_present = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                cpu_time=Sum('cpu_time'),
                wait_time=Sum('wait_time'),
                wall_time=Sum('wall_time'),
                number_jobs=Sum('number_jobs')
            ).order_by('month')

            # Parse to present results
            if results_to_present:
                cpu_time_to_present, wait_time_to_present, wall_time_to_present = self._parse_per_job_avg_result_set(
                    results_to_present
                )
                data['avg_cpu_time_to_present'] = round(mean(cpu_time_to_present), 2)
                data['avg_wait_time_to_present'] = round(mean(wait_time_to_present), 2)
                data['avg_wall_time_to_present'] = round(mean(wall_time_to_present), 2)
        except Exception:
            data = {}
        return data

    def _parse_core_count_node_utilisation_result_set(self, result_set):
        '''
        Return number processors and avg core per job for a
        given result_set.
        '''
        number_processors = []
        number_jobs = []
        avg_cores_per_job = []
        for row in result_set:
            number_processors.append(row['number_processors'])
            number_jobs.append(row['number_jobs'])
            avg_cores_per_job.append(round(row['number_processors'] / row['number_jobs'], 2))
        return number_processors, number_jobs, avg_cores_per_job

    def core_count_node_utilisation(self):
        '''
        Return the number of cores used and average cores per job for a date range.
        '''
        try:
            # Query number of cores in date range
            results_in_date_range = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                number_processors=Sum(F('number_jobs') * F('number_processors')),
                number_jobs=Sum('number_jobs'),
            ).order_by('month')

            # Parse date range results
            data = {}
            if results_in_date_range:
                data['dates'] = [row['month'].strftime('%b %Y') for row in results_in_date_range]
                number_processors, number_jobs, avg_cores_per_job = self._parse_core_count_node_utilisation_result_set(
                    results_in_date_range
                )
                data['num_processors'] = number_processors
                data['avg_cores_per_job'] = avg_cores_per_job
                data['num_processors_in_date_range'] = sum(number_processors)
                data['avg_cores_per_job_in_date_range'] = round(sum(number_processors) / sum(number_jobs), 2)

            # Query number of cores to present
            results_to_present = ComputeDaily.objects.filter(
                project=self.project,
                partition__in=self.partition_ids,
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                number_processors=Sum(F('number_jobs') * F('number_processors')),
                number_jobs=Sum('number_jobs'),
            ).order_by('month')

            # Parse to present results
            if results_to_present:
                number_processors_to_present, number_jobs_to_present, _ = self._parse_core_count_node_utilisation_result_set(
                    results_to_present
                )
                data['num_processors_to_present'] = sum(number_processors_to_present)
                data['avg_cores_per_job_to_present'] = round(
                    sum(number_processors_to_present) / sum(number_jobs_to_present), 2
                )
        except Exception:
            data = {}
        return data

    def total_core_hours(self):
        '''
        Return the total number of elapsed core hours consumed over all time.
        '''
        result = ComputeDaily.objects.filter(project=self.project).aggregate(wall_time=Sum('wall_time'))['wall_time']
        return result if result else 0

    def total_cpu_hours(self):
        '''
        Return the total number of CPU hours consumed over all time.
        '''
        result = ComputeDaily.objects.filter(project=self.project).aggregate(cpu_time=Sum('cpu_time'))['cpu_time']
        return result if result else 0

    def total_wait_time(self):
        result = ComputeDaily.objects.filter(project=self.project).aggregate(wait_time=Sum('wait_time'))['wait_time']
        return result if result else 0

    def efficiency(self):
        '''
        Return the overall project efficiency (CPU/Elapsed).
        '''
        try:
            return (self.total_cpu_hours() / self.total_core_hours())
        except ZeroDivisionError:
            return 0

    def total_slurm_jobs(self):
        '''
        Return the total number of jobs run through Slurm over all time.
        '''
        result = ComputeDaily.objects.filter(project=self.project
                                            ).aggregate(number_jobs=Sum('number_jobs'),)['number_jobs']
        return result if result else 0

    def partition_stats_in_date_range(
        self,
        start_date=None,
        end_date=None,
        partition_type=[Partition.CORE],
    ):
        '''
        Return the compute stats for project for a given date range and
        partition.
        '''
        # Use dates when instance was created, if not supplied
        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date
        else:
            end_date = end_date + datetime.timedelta(days=1)

        data = {
            'cpu_time': 0,
            'wait_time': 0,
            'wall_time': 0,
        }

        data['cpu_time'] = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type__in=partition_type,
            date__range=[start_date, end_date],
        ).aggregate(cpu_time=Sum('cpu_time'))['cpu_time']

        data['wait_time'] = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type__in=partition_type,
            date__range=[start_date, end_date],
        ).aggregate(wait_time=Sum('wait_time'))['wait_time']

        data['wall_time'] = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type__in=partition_type,
            date__range=[start_date, end_date],
        ).aggregate(wall_time=Sum('wall_time'))['wall_time']

        return data
