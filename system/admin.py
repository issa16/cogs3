from django.contrib import admin

from system.models import Phase
from system.models import System
from system.models import SystemToInstitutionMap
from system.models import OperatingSystem
from system.models import Queue


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'number',
        'description',
        'modified_time',
    )


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


@admin.register(SystemToInstitutionMap)
class SystemToInstitutionMapAdmin(admin.ModelAdmin):
    list_display = (
        'system',
        'institution',
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
