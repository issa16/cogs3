from django.contrib import admin

from system.models import System
from system.models import OperatingSystem
from system.models import Queue
from system.models import Cluster


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'number_of_cores',
    )
    search_fields = (
        'name',
        'description',
    )


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'modified_time',
    )


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'cluster',
        'os',
        'cores_per_node',
        'modified_time',
    )


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'total_number_of_cores',
        'system',
        'modified_time',
    )
