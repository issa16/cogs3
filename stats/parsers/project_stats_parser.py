import datetime

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from project.models import ProjectUserMembership
from stats.models import ComputeDaily, StorageWeekly
from system.models import Partition

# -----------------------------------------------------------------------------
# Work in progress - AO
# -----------------------------------------------------------------------------


class ProjectStatsParser:

    def __init__(
        self,
        project,
        start_date,
        end_date,
    ):
        self.project = project
        self.start_date = start_date
        self.end_date = end_date + datetime.timedelta(days=1)

    def pi_projects(self):
        data = [
            ['Active', 0],
            ['Dormant', 0],
            ['Inactive', 0],
            ['Retired', 0],
        ]
        return data

    def user_status(self):
        try:
            '''
            Active count - Defined by current project membership active
            '''
            active_users = ProjectUserMembership.objects.filter(
                project=self.project,
                status=ProjectUserMembership.AUTHORISED,
            ).count()
            '''
            Dormant count - Defined by current project membership active but no
            usage for X months.
            '''
            dormant_users = 0
            '''
            Inactive count - Defined by current project membership revoked or
            suspended.
            '''
            inactive_users = ProjectUserMembership.objects.filter(
                Q(status=ProjectUserMembership.REVOKED) | Q(status=ProjectUserMembership.SUSPENDED),
                project=self.project,
            ).count()

            data = [
                ['Active', active_users],
                ['Dormant', dormant_users],
                ['Inactive', inactive_users],
            ]
            return data
        except Exception:
            pass
        return []

    def rate_of_usage(self):
        return 0

    def cumlative_usage(self):
        return 0

    def individual_user_usage(self):
        return 0

    def usage_by_partition(self):
        return 0

    def num_jobs_per_month(self):
        return 0

    def per_job_avg_stats(self):
        return 0

    def core_count_node_utilisation(self):
        return 0

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

    def efficency(self):
        '''
        Return the overall project efficency (CPU/Elapsed).
        '''
        try:
            return (self.total_cpu_hours() / self.total_core_hours()) * 100
        except ZeroDivisionError:
            return 0

    def total_slurm_jobs(self):
        '''
        Return the total number of jobs run through Slurm over all time.
        '''
        result = ComputeDaily.objects.filter(project=self.project
                                            ).aggregate(number_jobs=Sum('number_jobs'),)['number_jobs']
        return result if result else 0

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    def partition_stats_in_date_range(
        self,
        start_date=None,
        end_date=None,
        partition=Partition.CORE,
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
            'cpu_time': 1,
            'wait_time': 1,
            'wall_time': 1,
        }

        data['cpu_time'] = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type=partition,
            date__range=[start_date, end_date],
        ).aggregate(cpu_time=Sum('cpu_time'))['cpu_time']

        data['wait_time'] = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type=partition,
            date__range=[start_date, end_date],
        ).aggregate(wait_time=Sum('wait_time'))['wait_time']

        data['wall_time'] = ComputeDaily.objects.filter(
            project=self.project,
            partition__partition_type=partition,
            date__range=[start_date, end_date],
        ).aggregate(wall_time=Sum('wall_time'))['wall_time']

        return data

    # -------------------------------------------------------------------------
    # Storage
    # -------------------------------------------------------------------------
    def storage_stats_in_date_range(
        self,
        start_date=None,
        end_date=None,
    ):
        '''
        Return disk space and file count stats for a given date range.
        '''
        # Use dates when instance was created, if not supplied
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

        # Disk space
        try:
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[start_date, end_date],
            ).aggregate(
                Avg('home_space_used'),
                Avg('scratch_space_used'),
            )
            data['home_space_used_avg'] = result['home_space_used__avg']
            data['scratch_space_used_avg'] = result['scratch_space_used__avg']
        except StorageWeekly.DoesNotExist:
            pass

        # File usage
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
        except StorageWeekly.DoesNotExist:
            return 0
        return data

    def disk_space(self):
        try:
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                home_space_used_sum=Sum('home_space_used'),
                scratch_space_used_sum=Sum('scratch_space_used'),
            ).order_by('month')

            dates = []
            home = []
            scratch = []
            total = []
            for row in result:
                dates.append(str(row['month']))
                home.append(row['home_space_used_sum'])
                scratch.append(row['scratch_space_used_sum'])
                total.append(row['home_space_used_sum'] + row['scratch_space_used_sum'])

            data = {
                'dates': dates,
                'home': home,
                'scratch': scratch,
                'total': total,
            }
            return data
        except Exception as e:
            print(e)
        return []

    def file_count(self):
        try:
            result = StorageWeekly.objects.filter(
                project=self.project,
                date__range=[self.start_date, self.end_date],
            ).annotate(month=TruncMonth('date')).values('month').annotate(
                c=Count('id'),
                home_files_used_sum=Sum('home_files_used'),
                scratch_files_used_sum=Sum('scratch_files_used'),
            ).order_by('month')

            dates = []
            home = []
            scratch = []
            total = []
            for row in result:
                dates.append(str(row['month']))
                home.append(row['home_files_used_sum'])
                scratch.append(row['scratch_files_used_sum'])
                total.append(row['home_files_used_sum'] + row['scratch_files_used_sum'])

            data = {
                'dates': dates,
                'home': home,
                'scratch': scratch,
                'total': total,
            }
            return data
        except Exception as e:
            print(e)
        return []
