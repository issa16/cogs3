from django.contrib import admin

from stats.models import ComputeDaily, StorageWeekly


@admin.register(ComputeDaily)
class ComputeDaily(admin.ModelAdmin):
    list_display = (
        'date',
        'user',
        'project',
        'number_jobs',
        'wait_time',
        'cpu_time',
        'wall_time',
        'created_time',
    )


@admin.register(StorageWeekly)
class StorageWeekly(admin.ModelAdmin):
    list_display = (
        'date',
        'project',
        'home_space_used',
        'home_files_used',
        'scratch_space_used',
        'scratch_files_used',
        'created_time',
    )
