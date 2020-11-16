from django.contrib import admin

from stats.models import Application
from stats.models import Theme
from stats.models import AccessMethod
from stats.models import NumberOfProcessors
from stats.models import DailyStat
from stats.models import WeeklyStatStorageProjectsCF


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'modified_time',
    )


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'distinguished_name',
        'modified_time',
    )


@admin.register(AccessMethod)
class AccessMethodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'modified_time',
    )


@admin.register(NumberOfProcessors)
class NumberOfProcessorsAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'modified_time',
    )


@admin.register(DailyStat)
class DailyStatAdmin(admin.ModelAdmin):
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


@admin.register(WeeklyStatStorageProjectsCF)
class WeeklyStatStorageProjectsCFAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'project',
        'home_space_used',
        'home_files_used',
        'scratch_space_used',
        'scratch_files_used',
        'created_time',
    )
